#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import
from __future__ import division

import sys
import os
import logging
import traceback
import socket
import re
import ConfigParser

import yagmail
import unicodecsv as csv
import xml.etree.ElementTree as etree

reload(sys)
sys.setdefaultencoding("utf-8")


logger = logging.getLogger("ganglia_alert")


ip_pattern = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}" + \
                        r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
def is_ip_addr(srcstr):
    """Judge if a string match an IPv4 form.
    Args:
        srcstr (str): Input string to be judged.
    Returns:
        bool: The return value. True for srcstr is formed in IPv4, False otherwise.
    """
    return True if ip_pattern.match(srcstr.strip()) is not None else False


def load_conf(conf_path):
    """Read an ini format configuration file and return an ConfigParser object.
    Args:
        conf_path (str): Absolute path of the configuration file.
    Returns:
        conf_loader (ConfigParser): A ConfigParser object contains
                                    all configuration keys and values.
    """
    conf_loader = ConfigParser.ConfigParser()
    conf_loader.read(conf_path)

    logger.debug("Read configuration from %s", conf_path)
    return conf_loader


def parse_rule(rule_path):
    """Read the rule file and return each rule.

       A rule file should be an DSV format file, fields seperated
       by colon, lines terminated by \n .

       fields' order:
       1 - target gridname
       2 - target clustername
       3 - target hostname or ip
       4 - target metricname
       5 - compare operator, support values:
           = , >= , > , <= , <
       6 - threshold value

    Args:
        rule_path (str): Absolute path of the rule file.
    Yields:
        tuple: (gridname, clustername, hostname or ip,
                metricname, compare operation, threshold value)
    """
    with open(rule_path, "rb") as f:
        rf = csv.reader(f, delimiter=':', encoding="utf-8")
        for each_line in rf:
            if each_line[0].startswith("#"):
                continue

            yield (each_line[0],
                   each_line[1],
                   str(each_line[2]),
                   each_line[3],
                   str(each_line[4]),
                   each_line[5])


class MailSender(object):
    """Agent sends alert emails.
    Attributes:
        mail_username (str): SMTP user name.
        mail_password (str): SMTP password or app token.
        mail_server_host (str): SMTP server hostname or ip.
        mail_server_port (str): SMTP server port.
    """
    def __init__(self, conf):
        self.mail_username = conf.get("email", "username")
        self.mail_password = conf.get("email", "password")
        self.mail_server_host = conf.get("email", "smtp_host")
        self.mail_server_port = conf.get("email", "smtp_port")

    def concat_addresses(self, addr_file):
        """Read email addresses from a text file, and concat them.

        In the email addresses file, each line should contain only one address.

        Args: 
            addr_file  (str): Absolute path of the email address file.
        Returns:
            str: A string contains all email addresses with semicolon.
        """
        recv_addr = []
        with open(addr_file, "rb") as f:
            for each_addr in f:
                if each_addr[0].strip().startswith("#"):
                    continue
                recv_addr.append(each_addr[0].replace(";").strip())

        return ";".join(recv_addr)


    def sendmail(self, mailto, subject, body):
        """Send an mail.
        Args:
            mailto (str): receive email addresses, seperated by comma.
            subject (str): subject of email.
            body (str): bodu of email.
        """
        try:
            yag = yagmail.SMTP(user=self.mail_username,
                               password=self.mail_password,
                               host=self.mail_server_host,
                               port=self.mail_server_port)
            yag.send(to=mailto, subject=subject, contents=body)
        except:
            logger.error(traceback.format_exc())


class GangliaQuery(object):
    """Query ganglia monitoring data from gmetad in XML format.
    Attributes:
        gmetad_host (str): IP of gmetad.
        gmetad_port (int): Port of gmetad.
    """
    def __init__(self, gmetad_host, gmetad_port=8651):
        self.gmetad_address = (gmetad_host, int(gmetad_port))


    def get_xml_info(self):
        """Get a xml content of all grids from gmetad."""
        socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_buffer = ""
        try:
            socket_client.connect(self.gmetad_address)
            while True:
                recv = socket_client.recv(8192)
                if not recv:
                    break
                data_buffer += recv
            return data_buffer
        except:
            logger.error(traceback.format_exc())
        finally:
            socket_client.close()


class GangliaInfo(object):
    """Parse ganglia XML monitoring data.
    Attributes:
        type_map (dict): Mapping types of ganglia metrics to python data type.
        xpath_mhcg (str): Xpath to get the metric value (Grid -> Cluster -> Hostname -> Metric).
        xpath_micg (str): Xpath to get the metric value (Grid -> Cluster -> IP -> Metric).
    """
    def __init__(self):
        self.type_map = {"double": float,
                         "float": float,
                         "inet16": int,
                         "inet32": int,
                         "string": str}

        self.xpath_mhcg = './GRID[@NAME="{gridname}"]' + \
                          '/CLUSTER[@NAME="{clustername}"]' + \
                          '//HOST[@NAME="{addr}"]' + \
                          '//METRIC[@NAME="{metricname}"]'

        self.xpath_micg = './GRID[@NAME="{gridname}"]' + \
                          '/CLUSTER[@NAME="{clustername}"]' + \
                          '//HOST[@IP="{addr}"]' + \
                          '//METRIC[@NAME="{metricname}"]'

    def parse_xml_info(self, xml_string, gridname, clustername, host, metricname):
        """Return a specific metric value.

           Note: All input parameter can be found on ganglia web dashboard.
        Args:
            xml_string (str): XML monitoring data.
            gridname (str): Target grid name defined in gmetad.
            clustername (str): Target cluster name defined in gmetad.
            host (str): Target hostname or IP.
            metricname (str): Target metric name.
        Returns:
            metric_value: Value of target metric name.
        """
        if (not isinstance(xml_string, str)) or xml_string is None:
            raise TypeError("No data from gmetad!")

        root = etree.fromstring(xml_string)
        target_xpath = None

        if is_ip_addr(host):
            target_xpath = self.xpath_micg
        else:
            target_xpath = self.xpath_mhcg


        target_node = root.find(target_xpath.format(gridname=gridname,
                                                    clustername=clustername,
                                                    addr=host,
                                                    metricname=metricname))

        metric_data_type = target_node.attrib["TYPE"].strip().lower()
        metric_value = self.type_map[metric_data_type](target_node.attrib["VAL"])
        logger.debug("Get xml:: %s/%s/%s/metric[ %s ] = %s", gridname,
                     clustername,
                     host,
                     metricname,
                     metric_value)

        return metric_value


    def should_alert_metric_value(self, metric_value, cmp_op, threshold):
        """Compare the metric value with threshold.
        Args:
            metric_value: Metric value got from gmetad.
            cmp_op (str): Compare operator, support values:
                          = , >= , > , <= , <
            threshold: Threshold value.
        Returns:
            bool: The return value, True for yes, False for no.
        """
        if cmp_op not in ('=' , '>=' , '>' , '<=' , '<'):
            raise ValueError("Unsupport compare operator {},".format(cmp_op) +
                             " valid values are: = , >= , > , <= and <.")

        try:
            try_compare = eval("{!s} {} {!s}".format(metric_value,
                                                     cmp_op,
                                                     threshold))
            logger.debug("Compare: %s %s %s , Result: %s, type %s",
                         metric_value,
                         cmp_op,
                         threshold,
                         try_compare,
                         type(try_compare))
            return try_compare
        except:
            logger.error(traceback.format_exc())

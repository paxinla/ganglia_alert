#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import
from __future__ import division

import sys
import os
import logging
import traceback
from datetime import datetime

from ganglia_alert.util import load_conf
from ganglia_alert.util import parse_rule
from ganglia_alert.util import MailSender
from ganglia_alert.util import GangliaQuery
from ganglia_alert.util import GangliaInfo

from ganglia_alert.spec import EMAIL_SUBJECT
from ganglia_alert.spec import EMAIL_BODY

reload(sys)
sys.setdefaultencoding("utf-8")

logFormatter = logging.Formatter('%(asctime)s [%(levelname)s] (%(pathname)s:%(lineno)d@%(funcName)s) -> %(message)s')
logger = logging.getLogger("ganglia_alert")
# Change this for the log level.
logger.setLevel(logging.INFO)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

ROOTDIR = os.path.abspath(os.path.dirname(__file__))
CONFIGFILE = os.path.join(ROOTDIR, "config.ini")


def process(rulefile_path, logfile_path=None):
    """Main process
    Args:
        rulefile_path (str): Absolute path of rule file.
        logfile_path (str): Absolute path of log file.
    """
    if logfile_path is not None:
        log_file_handler = logging.FileHandler(os.path.join(
            logfile_path,
            "Alert_{}.log".format(datetime.now().\
                                  isoformat()[:10].\
                                  replace('-', ''))))
        log_file_handler.setFormatter(logFormatter)
        logger.addHandler(log_file_handler)

    config = load_conf(CONFIGFILE)
    mailsender = MailSender(config)
    query_ganglia = GangliaQuery(config.get("ganglia", "gmetad_host"),
                                 config.get("ganglia", "gmetad_port"))
    ganglia_info = GangliaInfo()

    for each_rule in parse_rule(rulefile_path):
        grid, cluster, host, metric, cmpop, threshold = each_rule
        xml_all_monitor_data = query_ganglia.get_xml_info()
        metric_value = ganglia_info.parse_xml_info(xml_all_monitor_data,
                                                   grid,
                                                   cluster,
                                                   host,
                                                   metric)
        should_alert = ganglia_info.should_alert_metric_value(metric_value,
                                                              cmpop,
                                                              threshold)

        if should_alert:
            mail_subject = EMAIL_SUBJECT.format(metricname=metric,
                                                host=host)
            mail_body = EMAIL_BODY.format(gridname=grid,
                                          clustername=cluster,
                                          host=host,
                                          metricname=metric,
                                          metricvalue=metric_value,
                                          metricop=cmpop,
                                          metricthreshold=threshold)
            mailsender.sendmail(config.get("email", "mailto").replace(' ', ''),
                                mail_subject,
                                mail_body)

# A little tool for monitoring ganglia metrics and send alert emails

## Requiments

- python2 (version >=2.7).
- a host that can connect to gmetad , this may require the host which this program running on should be in trusted_hosts of gmetad(default: /etc/ganglia/gmetad.conf).

## Install

1. Edit ganglia_alert/config.ini.
2. execute:
   ```shell
   $ make clean
   $ make
   $ sudo make install
   ```

## Usage

```shell
$ ganglia_alert --rule AbsolutePathOfTheRuleFile --mailto AbsolutePathOfTheMailAddressFile
```

## Mail address file

A mail address file is a text file, each line in it is a target email address. Program will send alert mail to all email addresses.

## Rule file

A rule file is a text file in DSV format. Each line is a rule and each field seperated by colon. A rule compare a specific ganglia metric value of a host with a given threshold. Accoding to the comprare result, it will send an alert email to your email addresses.

A rule file example:

```
my_grid_name:my_cluster_name:host_a_name:disk_free_percent_data:<:30.0
my_grid_name:my_cluster_name:host_b_name:disk_free_percent_opt:<:20.0
```

## Log file

Log only print to stdin default. If you need a log file , just use option --logfile .


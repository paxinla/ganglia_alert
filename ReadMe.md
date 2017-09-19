# A little tool for monitoring ganglia metrics and send alert emails

## Requiments

- python2 (version >=2.7).
- a host that can connect to gmetad , this may require the host which this program running on should be in trusted_hosts of gmetad(default: /etc/ganglia/gmetad.conf).

## Install

1. Edit ganglia_alert/config.ini.
2. execute:
   ```shell
   $ python setup.py build
   $ python setup.py sdist
   $ python setup.py bdist_egg
   ```
   then a .egg file will be generated under the *dist* directory. 
3. execute:
   ```shell
   $ sudo easy_install dist/*.egg
   ```

## Usage

```shell
$ ganglia_alert --rule AbsolutePathOfTheRuleFile
```

## Rule file

A rule file is a text file in DSV format. Each line is a rule and each field seperated by colon. A rule compare a specific ganglia metric value of a host with a given threshold. Accoding to the comprare result, it will send an alert email to your email addresses.

A rule file example:

```
my_grid_name:my_cluster_name:host_a_name:disk_free_percent_data:<:30.0
my_grid_name:my_cluster_name:host_b_name:disk_free_percent_opt:<:20.0
```


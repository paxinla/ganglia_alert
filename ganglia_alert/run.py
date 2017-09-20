#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import
from __future__ import division


import sys
import os
import traceback
import argparse

from ganglia_alert.core import process

reload(sys)
sys.setdefaultencoding("utf-8")


def parse_input():
    parser = argparse.ArgumentParser(description="Scan ganglia metrics and alert tool.")

    parser.add_argument("--rule", dest="rule_path", type=str, required=True,
                        help="[Required]Absolute path of the rule file.")
    parser.add_argument("--mailto", dest="mailto_path", type=str, required=True,
                        help="[Required]Absolute path of the email addresses list file.")
    parser.add_argument("--logfile", dest="logfile_path", type=str, required=False,
                        help="[Optional]Absolute path of the log file.")
    parser.add_argument("--loglevel", dest="log_level", type=str, required=False,
                        choices=("debug", "info", "error"),
                        help="[Optional]Log level, default is info.")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    return vars(parser.parse_args())


def main():
    in_args = parse_input()
    process(in_args["rule_path"],
            in_args["mailto_path"],
            in_args["log_level"],
            in_args["logfile_path"])


if __name__ == "__main__":
    main()

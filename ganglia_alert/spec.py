#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import
from __future__ import division

import sys

reload(sys)
sys.setdefaultencoding("utf-8")


EMAIL_SUBJECT = "[Ganglia][Warnning]Host: {host}"

EMAIL_BODY = """
- Target Host: {gridname} -> {clustername} -> {host}
- Target Metric: {metricname}

> Metric current: {metricvalue}
- Monitor operator: {metricop}
- Metric threshold: {metricthreshold}

-------------------------------------------------------
"""

EMAIL_TAIL = """
=======================================================
This mail sended by alert program, do not reply please.
"""

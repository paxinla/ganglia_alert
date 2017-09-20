#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import

import os
from setuptools import setup, find_packages

ROOTDIR = os.path.abspath(os.path.dirname(__file__))

def requirements():
    pip_reqf = os.path.join(os.path.abspath(os.path.dirname(__file__)), "requirements.txt")
    reqs = []
    with open(pip_reqf, "rb") as f:
        for each_line in f:
            if each_line.startswith("-f"):
                continue
            reqs.append(each_line.strip())
    return reqs


setup(
    name='ganglia_alert',
    version='0.1.dev0',
    description='A little tool for monitoring ganglia metrics and send alert emails',
    long_description=open('ReadMe.md').read(),
    author="paxinla",
    license="MIT",
    packages=find_packages(),
    package_data={"ganglia_alert": ["config.ini"]},
    install_requires=requirements(),
    keywords='ganglia email alert',
    classifiers=[
           'Development Status :: 3 - Alpha',
           'Intended Audience :: Developers',
           'Intended Audience :: System Administrators',
           'Topic :: System :: Systems Administration',
           'License :: OSI Approved :: MIT License',
           'Programming Language :: Python :: 2',
           'Programming Language :: Python :: 2.7'
    ],
    entry_points={
        'console_scripts': [
            'ganglia_alert=ganglia_alert.run:main',
        ],
    }
)

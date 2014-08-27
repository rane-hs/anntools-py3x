#!/usr/bin/python

import os
import re
from distutils.core import setup

def loadVersion():
    version_regexp = re.compile(r'__version__\s*=\s*(\(.*?\))', re.M)
    version_file = open('anntools/version.py', 'rb').read()
    version_match = version_regexp.search(version_file)
    return eval(version_match.group(1))
    
version = loadVersion()
version_number = '.'.join([str(x) for x in version])

setup(
    name         = "anntools",
    version      = version_number,
    author       = "Viktor Ferenczi",
    author_email = "python@cx.hu",
    url          = "http://python.cx.hu",
    #download_url = "http://cheeseshop.python.org/pypi/anntools/%s"%version_number,
    download_url = "http://python.cx.hu/anntools/anntools-%s.tar.gz"%version_number,
    description  = "Validation and type conversion tools based on function annotation",
    long_description = open('README', 'r').read(),
    license      = "LGPL",
    platforms    = ["Platform Independent"],
    classifiers  = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    packages = [
        "anntools",
    ],
)

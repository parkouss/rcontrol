# -*- coding: utf-8 -*-

from setuptools import setup
import os
import re


THIS_DIR = os.path.dirname(os.path.realpath(__name__))


def read(*parts):
    with open(os.path.join(THIS_DIR, *parts)) as f:
        return f.read()


def get_version():
    return re.findall("__version__ = '([\d\.]+)'",
                      read('rcontrol', '__init__.py'), re.M)[0]


setup(
    name='rcontrol',
    version=get_version(),
    description="python API to execute asynchronous remote tasks with ssh",
    long_description=read("README.rst"),
    author=u"Julien Pagès",
    author_email="j.parkouss@gmail.com",
    install_requires=['six', 'paramiko'],
    url='http://github.com/parkouss/rcontrol',
    license="GPL 2.0/LGPL 2.1",
    packages=['rcontrol'],
    platforms=['Any'],
)

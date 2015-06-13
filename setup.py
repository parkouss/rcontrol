# -*- coding: utf-8 -*-

# This file is part of rcontrol.
#
# rcontrol is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# rcontrol is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with rcontrol. If not, see <http://www.gnu.org/licenses/>.

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
    license="LGPL",
    packages=['rcontrol'],
    platforms=['Any'],
    tests_require=['mock'],
    test_suite="tests",
)

**rcontrol**
============

.. image:: https://travis-ci.org/parkouss/rcontrol.svg?branch=master
    :target: https://travis-ci.org/parkouss/rcontrol
.. image:: https://coveralls.io/repos/parkouss/rcontrol/badge.svg?branch=master
    :target: https://coveralls.io/r/parkouss/rcontrol?branch=master

.. image:: https://readthedocs.org/projects/rcontrol/badge/?version=latest
    :target: https://readthedocs.org/projects/rcontrol/?badge=latest
    :alt: Documentation Status


**rcontrol** is a python library based on **paramiko** intended to work
with remote machines via ssh.

Unlike **fabric**, it is intended to perform tasks in an asynchronous way,
and to work with python >= 2.7 (including **python 3**).

Please note that this is under development! I am waiting for feedback,
ideas and contributors to make this tool evolve.

Basic example:

.. code-block:: python

  from rcontrol.ssh import SshSession, ssh_client
  from rcontrol.core import SessionManager

  def log(task, line):
      print("%r: %s" % (task, line))

  with SessionManager() as sessions:
      # create sessions on two hosts
      sessions.bilbo = SshSession(
          ssh_client('http://bilbo.domain.com', 'user', 'pwd'))
      sessions.nazgul = SshSession(
          ssh_client('http://nazgul.domain.com', 'user', 'pwd'))

      # run commands in parallel
      sessions.bilbo.execute("uname -a && sleep 3", on_stdout=log)
      sessions.nazgul.execute("uname -a && sleep 3", on_stdout=log)

This example just show you how **rcontrol** looks like. Look at the
documentation on http://rcontrol.readthedocs.org/en/latest/ if you're
interested to see more!


What **rcontrol** can do
========================

* execute multiple commands on local and remote hosts in an asynchronous way
  (it is up to you to synchronize them)

* define timeout and output timeout for the commands

* attach callbacks when a line is read (stdout or stderr), on timeout and
  when the commands are finished

* copy files and directories from one host to another


What **rcontrol** needs (contributors, you're welcome!)
=======================================================

* be able to stop (kill) a command (local or remote)

* more file operations

* love


How to install
==============

Use pip. ::

  pip install -U rcontrol


Changelog
=========

See the CHANGELOG.rst file.

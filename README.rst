**rcontrol**
============

**rcontrol** is a python library based on **paramiko** intended to work
with remote machines via ssh.

Unlike **fabric**, it is intended to perform tasks in an asynchronous way.

Please note that this is under development! I am waiting for feedback,
ideas and contributors to make this tool evolve.

Basic example: ::

  from rcontrol.ssh import SshSession, ssh_client

  # create session on two hosts
  bilbo = SshSession(ssh_client('http://bilbo.domain.com', 'user', 'pwd'))
  nazgul = SshSession(ssh_client('http://nazgul.domain.com', 'user', 'pwd'))

  # run commands in parallel
  tasks = (bilbo.execute("uname -a && sleep 3"),
           nazgul.execute("uname -a && sleep 3"))

  # wait for both commands to finish
  for task in tasks:
      task.wait()

This example just show you how **rcontrol** looks like.


What **rcontrol** can do
========================

* execute multiple commands on local and remote hosts in an asynchronous way
  (it is up to you to synchronize them)

* define timeout and output timeout for the commands

* attach callbacks when a line is read (stdout or stderr), on timeout and
  when the commands are finished

* copy files from one host to another


What **rcontrol** needs (contributors, you're welcome!)
=======================================================

* be able to stop (kill) a command (local or remote)

* more file operations (create dirs, recursively copy dirs, remove, ...)

* make it work with python 3

* love


How to install
==============

Use pip. ::

  pip install -U rcontrol

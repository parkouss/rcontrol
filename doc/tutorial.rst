Tutorial
========

Learning guide for basic usage of **rcontrol**.

Executing a command on a remote host
------------------------------------

.. code-block:: python

  from rcontrol.ssh import ssh_client, SshSession

  # create a ssh connection. This basically create a connected
  # paramiko.SSHClient instance.
  conn = ssh_client('localhost', 'jp', 'jp')

  # execute the command
  with SshSession(conn) as session:
      session.execute("uname -a")

  # outside the with statement, all tasks are done and the connection
  # is automatically closed.


If you ran this snippet, you will see nothing on the screen. This is
because there is no handler defined for the command output:

.. code-block:: python

  from rcontrol.ssh import ssh_client, SshSession

  def on_finished(task):
      print("finished (exit code: %d) !" % task.exit_code())

  def on_output(task, line):
      print("output: %s" % line)

  conn = ssh_client('localhost', 'jp', 'jp')

  with SshSession(conn) as session:
      session.execute("uname -a", stdout_callback=on_output,
                      finished_callback=on_finished)


Output: ::

  output: Linux JP-Precision-T1500 3.13.0-39-generic #66-Ubuntu SMP Tue Oct 28 13:30:27 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux
  finished (exit code: 0) !


Synchronizing commands
----------------------

Here is an example of how to synchronize tasks. Tt run two commands in
parallel, then wait for them to finish an run a last command after that:

.. code-block:: python

  from rcontrol.ssh import ssh_client, SshSession

  conn = ssh_client('localhost', 'jp', 'jp')

  with SshSession(conn) as session:
      # this will run in parallel
      task1 = session.execute("sleep 1; touch /tmp/rcontrol1.test")
      task2 = session.execute("sleep 1; touch /tmp/rcontrol2.test")

      # now wait for them
      task1.wait()
      task2.wait()

      # and do something else
      session.execute("rm /tmp/rcontrol{1,2}.test")
      # no need to wait for this task, it will be done automatically
      # since we are in the with block

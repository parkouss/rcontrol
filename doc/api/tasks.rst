Tasks
=====

A task represent an action done locally or on remote hosts. All tasks
are asynchronous.

Abstract Task
-------------

.. autoclass:: rcontrol.core.Task
  :members:


CommandTask
-----------

.. inheritance-diagram:: rcontrol.core.CommandTask

.. autoclass:: rcontrol.core.CommandTask
  :members:


SshExec
-------

.. inheritance-diagram:: rcontrol.ssh.SshExec

.. autoclass:: rcontrol.ssh.SshExec
  :members:


LocalExec
---------

.. inheritance-diagram:: rcontrol.local.LocalExec

.. autoclass:: rcontrol.local.LocalExec
  :members:


ThreadableTask
--------------

.. inheritance-diagram:: rcontrol.core.ThreadableTask

.. autoclass:: rcontrol.core.ThreadableTask
  :members:


Task exceptions
---------------

.. autoclass:: rcontrol.core.BaseTaskError

.. autoclass:: rcontrol.core.TimeoutError

.. autoclass:: rcontrol.core.ExitCodeError

.. autoclass:: rcontrol.core.TaskErrors

.. _api-tasks:

Tasks
=====

A task represent an action done locally or on remote hosts. All tasks
are asynchronous.

.. currentmodule:: rcontrol.core

Abstract Task
-------------

.. autoclass:: Task
  :members:


CommandTask
-----------

.. inheritance-diagram:: CommandTask

.. autoclass:: CommandTask
  :members:

SshExec
-------

.. currentmodule:: rcontrol.ssh

.. inheritance-diagram:: SshExec

.. autoclass:: SshExec
  :members:


LocalExec
---------

.. currentmodule:: rcontrol.local

.. inheritance-diagram:: LocalExec

.. autoclass:: LocalExec
  :members:


.. currentmodule:: rcontrol.core

ThreadableTask
--------------

.. inheritance-diagram:: ThreadableTask

.. autoclass:: ThreadableTask
  :members:


Task exceptions
---------------

.. autoclass:: BaseTaskError

.. autoclass:: TimeoutError

.. autoclass:: ExitCodeError

.. autoclass:: TaskErrors

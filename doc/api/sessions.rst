.. _api-sessions:

Sessions
========

A session represent a connection on a remote or local machine.

.. currentmodule:: rcontrol.core

BaseSession
-----------

.. autoclass:: BaseSession
  :members:


SshSession
----------

.. currentmodule:: rcontrol.ssh

.. inheritance-diagram:: SshSession

.. autoclass:: SshSession
  :members:


.. autofunction:: ssh_client


LocalSession
------------

.. currentmodule:: rcontrol.local

.. inheritance-diagram:: LocalSession

.. autoclass:: LocalSession
  :members:


.. currentmodule:: rcontrol.core


SessionManager
--------------

.. autoclass:: SessionManager
  :members:

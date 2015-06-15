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

import subprocess
import os
import six

from rcontrol.streamreader import StreamsReader
from rcontrol.core import CommandTask, BaseSession


class ProcessReader(StreamsReader):
    """
    Specialized reader for subprocess.Popen instances.
    """
    def _create_readers(self, queue, proc):
        stdout_reader = None
        if proc.stdout:
            stdout_reader = self._create_stream_reader(proc.stdout,
                                                       queue,
                                                       self.stdout_callback)
        stderr_reader = None
        if proc.stderr and proc.stderr != proc.stdout:
            stderr_reader = self._create_stream_reader(proc.stderr,
                                                       queue,
                                                       self.stderr_callback)
        return stdout_reader, stderr_reader


class LocalExec(CommandTask):
    """
    Execute a local command.

    The execution starts as soon as the object is created.

    Basically extend a :class:`CommandTask` to pass in a specialized
    stream reader, :class:`ProcessReader`.

    :param session: instance of the :class:`LocalSession` responsible of
        this command execution
    :param command: the command to execute (a string)
    :param kwargs: list of argument passed to the base class constructor
    """
    def __init__(self, session, command, **kwargs):
        CommandTask.__init__(self, session, ProcessReader, command, **kwargs)
        stdout = subprocess.PIPE
        stderr = subprocess.STDOUT if self._combine_stderr else subprocess.PIPE
        self._proc = subprocess.Popen(command, shell=True, stdout=stdout,
                                      stderr=stderr)
        self._reader.start(self._proc)

    def _on_finished(self):
        if not self.timed_out():
            self._set_exit_code(self._proc.wait())
        CommandTask._on_finished(self)


@six.python_2_unicode_compatible
class LocalSession(BaseSession):
    """
    A session on the local machine.
    """
    def __str__(self):
        return "<LocalSession>"

    def open(self, filename, mode='r', bufsize=-1):
        return open(filename, mode=mode)

    def execute(self, command, **kwargs):
        return LocalExec(self, command, **kwargs)

    def walk(self, top, topdown=True, onerror=None, followlinks=False):
        os.walk(top, topdown=topdown, onerror=onerror, followlinks=followlinks)

    def mkdir(self, path):
        os.mkdir(path)

    def exists(self, path):
        return os.path.exists(path)

    def islink(self, path):
        return os.path.islink(path)

    def isdir(self, path):
        return os.path.isdir(path)

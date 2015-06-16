# -*- coding: utf-8

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

import sys
import threading
import six
from collections import OrderedDict
from rcontrol import fs
import abc
import warnings


class BaseTaskError(Exception):
    """Raised on a task error. All tasks errors inherit from this."""


class TaskError(BaseTaskError):
    """Raised on a task error"""
    def __init__(self, session, task, msg):
        self.session = session
        self.task = task
        self.rawmsg = msg
        BaseTaskError.__init__(self, "%s: %s (%s)" % (session, task, msg))


class TimeoutError(TaskError):
    """Raise on a command timeout error"""


class ExitCodeError(TaskError):
    """Raised when the exit code of a command is unexpected"""


class TaskErrors(BaseTaskError):
    """A list of task errors"""
    def __init__(self, errors):
        self.errors = errors
        BaseTaskError.__init__(self, '\n'.join(str(e) for e in self.errors))


@six.add_metaclass(abc.ABCMeta)
class Task(object):
    def __init__(self, session):
        self.session = session
        self.explicit_wait = False
        # register the task instance to the session
        session._register_task(self)

    def _unregister(self):
        # this must be called by subclasses when the task needs to be
        # unregistered from the session. This is called from a thread,
        # when the task is finished (or for a timeout)
        self.session._unregister_task(self)

    @abc.abstractmethod
    def is_running(self):
        """
        Return True if the task is running.
        """

    @abc.abstractmethod
    def error(self):
        """
        Return an instance of a :class:`BaseTaskError` or None.
        """

    def raise_if_error(self):
        """
        Check if an error occured and raise it if any.
        """
        error = self.error()
        if error:
            raise error

    @abc.abstractmethod
    def _wait(self, raise_if_error):
        pass

    def wait(self, raise_if_error=True):
        """
        Block and wait until the task is finished.

        :param raise_if_error: if True, call :meth:`raise_if_error` at
            the end.
        """
        self.explicit_wait = True
        return self._wait(raise_if_error=raise_if_error)


def _async(meth, name):
    def new_meth(self, *args, **kwargs):
        return ThreadableTask(self, meth, (self,) + args, kwargs)
    new_meth.__name__ = name
    new_meth.__doc__ = """
    Asynchronous version of :meth:`%s`.

    This method returns an instance of a :class:`ThreadableTask`.
""" % meth.__name__
    return new_meth


@six.add_metaclass(abc.ABCMeta)
class BaseSession(object):
    """
    Represent an abstraction of a session on a remote or local machine.

    Note that you should not use a session instance from multiple threads. For
    example, running commands and calling :meth:`wait_for_tasks` in parallel
    will have an undefined behaviour.
    """

    def __init__(self, auto_close=True):
        # a lock for tasks and silent errors access
        self._lock = threading.Lock()
        self._tasks = []
        # silent errors are errors from tasks that are not waited
        # explicitly. As a task is unregistered from the session once
        # it is finished, we save in this list the errors of tasks
        # that are finished before wait_for_tasks is called.
        self._silent_errors = []
        self.auto_close = auto_close

    def _register_task(self, task):
        assert isinstance(task, Task)
        with self._lock:
            self._tasks.append(task)

    def _unregister_task(self, task):
        with self._lock:
            try:
                self._tasks.remove(task)
            except ValueError:
                pass  # this should not happen
            # keep silent error
            if not task.explicit_wait:
                error = task.error()
                if error:
                    self._silent_errors.append(error)

    def tasks(self):
        """
        Return a copy of the currently active tasks.
        """
        with self._lock:
            return self._tasks[:]

    def wait_for_tasks(self, raise_if_error=True):
        """
        Wait for the running tasks launched from this session.

        If any errors are encountered, they are raised or returned depending
        on **raise_if_error**. Note that this contains errors reported from
        silently finished tasks (tasks ran and finished in backround without
        explicit wait call on them).

        Tasks started from another task callback (like on_finished)
        are also waited here.

        This is not required to call this method explictly if you use the
        :class:`BaseSession` or the :class:`SessionManager` with the **with**
        keyword.

        :param raise_if_error: If True, errors are raised using
            :class:`TaskErrors`. Else the errors are returned as a list.
        """
        errors = []
        # in case tasks do not unregister themselves we do not want to
        # loop infinitely
        tasks_seen = set()
        # we do a while loop to ensure that tasks started from callbacks
        # are waited too.
        while True:
            with self._lock:
                # bring back to life silent errors
                errors.extend(self._silent_errors)
                tasks = set(self._tasks)
            tasks = tasks - tasks_seen
            if not tasks:
                with self._lock:
                    # now clean the silent errors
                    self._silent_errors = []
                break
            for task in tasks:
                task.wait(raise_if_error=False)
                error = task.error()
                if error:
                    errors.append(error)
            with self._lock:
                # now clean the silent errors
                self._silent_errors = []
            tasks_seen.update(tasks)
        if raise_if_error and errors:
            raise TaskErrors(errors)
        return errors

    @abc.abstractmethod
    def open(self, filename, mode='r', bufsize=-1):
        """
        Return an opened file object.

        :param filename: the file path to open
        :param mode: the mode used to open the file
        :param bufsize: buffer size
        """

    @abc.abstractmethod
    def execute(self, command, **kwargs):
        """
        Execute a command in an asynchronous way.

        Return an instance of a subclass of a :class:`CommandTask`.

        :param command: the command to execute (a string)
        :param kwargs: named arguments passed to the constructor of the
            class:`CommandTask` subclass.
        """

    @abc.abstractmethod
    def walk(self, top, topdown=True, onerror=None, followlinks=False):
        """
        Walk the file system. Equivalent to os.walk.
        """

    @abc.abstractmethod
    def mkdir(self, path):
        """
        Create a directory. Equivalent to os.mkdir.
        """

    @abc.abstractmethod
    def exists(self, path):
        """
        Return True if the path exists. Equivalent to os.path.exists.
        """

    @abc.abstractmethod
    def isdir(self, path):
        """
        Return True if the path is a directory. Equivalent to os.path.isdir.
        """

    @abc.abstractmethod
    def islink(self, path):
        """
        Return True if the path is a link. Equivalent to os.path.islink.
        """

    def s_copy_file(self, src, dest_os, dest, chunk_size=16384):
        """
        Copy a file from this session to another session.

        :param src: full path of the file to copy in this session
        :param dest_os: session to copy to
        :param dest: full path of the file to copy in the dest session
        """
        fs.copy_file(self, src, dest_os, dest, chunk_size=chunk_size)

    copy_file = _async(s_copy_file, "copy_file")

    def s_copy_dir(self, src, dest_session, dest, chunk_size=16384):
        """
        Recursively copy a directory from a session to another one.

        **dest** must not exist, it will be created automatically.

        :param src: path of the dir to copy in this session
        :param dest_session: session to copy to
        :param dest: path of the dir to copy in the dest session (must
            not exists)
        """
        fs.copy_dir(self, src, dest_session, dest, chunk_size=chunk_size)

    copy_dir = _async(s_copy_dir, "copy_dir")

    def close(self):
        """
        Close the session.
        """

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        errors = self.wait_for_tasks(raise_if_error=False)
        if self.auto_close:
            self.close()
        if errors:
            if value is None:
                # no exceptions in the with block -> let's raise
                # the errors
                raise TaskErrors(errors)
            else:
                # TODO: for now, just print errors if any
                for error in errors:
                    print('ERROR: %s' % error)


class SessionManager(OrderedDict):
    """
    A specialized OrderedDict that keep sessions instances.

    It can be used like a namespace: ::

      sess_manager.local = LocalSession()
      # equivalent to:
      # sess_manager['local'] = LocalSession()

    It should be used inside a **with** block, to wait for pending
    tasks and close sessions if needed automatically.
    """

    def __setitem__(self, name, value):
        if not isinstance(name, six.string_types):
            raise TypeError('key must be an str instance')
        if not isinstance(value, BaseSession):
            raise TypeError('only BaseSession instances can be set')
        OrderedDict.__setitem__(self, name, value)

    def __setattr__(self, name, value):
        if isinstance(value, BaseSession):
            self[name] = value
        else:
            self.__dict__[name] = value

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError('%r does not exists' % name)

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            OrderedDict.__delattr__(self, name)

    def wait_for_tasks(self, raise_if_error=True):
        """
        Wait for the running tasks lauched from the sessions.
        """
        errors = []
        for session in self.values():
            errs = session.wait_for_tasks(raise_if_error=False)
            errors.extend(errs)
        if raise_if_error and errors:
            raise TaskErrors(errors)
        return errors

    def close(self):
        """
        close the sessions.
        """
        for session in self.values():
            session.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        errors = self.wait_for_tasks(raise_if_error=False)
        for session in self.values():
            if session.auto_close:
                session.close()
        if errors:
            if value is None:
                # no exceptions in the with block -> let's raise
                # the errors
                raise TaskErrors(errors)
            else:
                # TODO: for now, just print errors if any
                for error in errors:
                    print('ERROR: %s' % error)


class CommandTask(Task):
    """
    Base class that execute a command in an asynchronous way.

    It uses an internal stream reader (a subclass of
    :class:`streamreader.StreamsReader`)

    :param session: the session that run this command
    :param reader_class: the :class:`streamreader.StreamsReader` class
        to use
    :param command: the command to execute (a string)
    :param expected_exit_code: the expected exit code of the command. If
        None, there is no exit code expected.
    :param combine_stderr: if None, stderr and stdout will be automatically
        combined unless stderr_callback is defined. You can force to combine
        stderr or stdout by passing True or False.
    :param timeout: timeout in seconds for the task. If None, no timeout is
        set - else timeout_callback is called if the command has not finished
        in time.
    :param output_timeout: timeout in seconds for waiting output. If None, no
        timeout is set - else timeout_callback is called if there is no output
        in time.
    :param on_finished: a callable that takes one parameter, the command
        task instance. Called when the command is finished, but not on timeout.
    :param on_timeout: a callable that takes one parameter, the command
        task instance. Called on timeout.
    :param on_stdout: a callable that takes two parameter, the command
        task instance and the line read. Called on line read from stdout and
        possibly from stderr if streams are combined..
    :param on_stderr: a callable that takes two parameter, the command
        task instance and the line read. Called on line read from stderr.
    """
    def __init__(self, session, reader_class, command, expected_exit_code=0,
                 combine_stderr=None, timeout=None, output_timeout=None,
                 on_finished=None, on_timeout=None, on_stdout=None,
                 on_stderr=None,
                 # deprecated aliases
                 finished_callback=None, timeout_callback=None,
                 stdout_callback=None, stderr_callback=None):
        Task.__init__(self, session)

        if combine_stderr is None:
            combine_stderr = not stderr_callback
        self._combine_stderr = combine_stderr

        self.__exit_code = None
        self.__expected_exit_code = expected_exit_code
        self.__timed_out = False

        def _warn(name):
            msg = ("You should use on_%s instead of %s_callback"
                   " in new code (it will be removed soon)") % (name, name)
            warnings.warn(msg)

        if finished_callback:
            _warn("finished")
            on_finished = finished_callback
        if timeout_callback:
            _warn("timeout")
            on_timeout = timeout_callback
        if stdout_callback:
            _warn("stdout")
            on_stdout = stdout_callback
        if stderr_callback:
            _warn("stderr")
            on_stderr = stderr_callback

        self.__finished_callback = on_finished
        self.__timeout_callback = on_timeout
        self.__stdout_callback = on_stdout
        self.__stderr_callback = on_stderr

        self._reader = reader_class(
            stdout_callback=self._on_stdout,
            stderr_callback=self._on_stderr,
            timeout=timeout,
            output_timeout=output_timeout,
            timeout_callback=self._on_timeout,
            finished_callback=self._on_finished
        )

    def _set_exit_code(self, exit_code):
        self.__exit_code = exit_code

    def _on_stdout(self, line):
        if self.__stdout_callback:
            self.__stdout_callback(self, line)

    def _on_stderr(self, line):
        if self.__stderr_callback:
            self.__stderr_callback(self, line)

    def _on_timeout(self):
        self._unregister()
        self.__timed_out = True
        if self.__timeout_callback:
            self.__timeout_callback(self)

    def _on_finished(self):
        self._unregister()
        if self.__finished_callback:
            self.__finished_callback(self)

    def timed_out(self):
        """
        Return True if a timeout occured.
        """
        return self.__timed_out

    def is_running(self):
        """
        Return True if the command is still running.
        """
        return self._reader.is_alive()

    def error(self):
        """
        Return an instance of Exception if any, else None.

        Actually check for a :class:`TimeoutError` or a
        :class:`ExitCodeError`.
        """
        if self.__timed_out:
            return TimeoutError(self.session, self, "timeout")
        if self.__exit_code is not None and \
                self.__expected_exit_code is not None and \
                self.__exit_code != self.__expected_exit_code:
            return ExitCodeError(self.session, self,
                                 'bad exit code: Got %s' % self.__exit_code)

    def exit_code(self):
        """
        Return the exit code of the command, or None if the command is
        not finished yet.
        """
        return self.__exit_code

    def _wait(self, raise_if_error):
        if self._reader.is_alive():
            self._reader.thread.join()
        if raise_if_error:
            self.raise_if_error()
        return self.__exit_code


class ThreadableTask(Task):
    """
    A task ran in a background thread.
    """
    def __init__(self, session, callable, args, kwargs,
                 finished_callback=None):
        Task.__init__(self, session)
        # Set up exception handling
        self.exception = None

        def wrapper(*args, **kwargs):
            try:
                callable(*args, **kwargs)
            except Exception:
                self.exception = TaskError(session, self, sys.exc_info()[1])
            finally:
                self._unregister()
                if finished_callback:
                    finished_callback(self)

        # Kick off thread
        name = getattr(callable, '__name__', None)
        thread = threading.Thread(None, wrapper, name, args, kwargs)
        thread.setDaemon(True)
        thread.start()
        # Make thread available to instantiator
        self.thread = thread

    def is_running(self):
        return self.thread.is_alive()

    def error(self):
        return self.exception

    def _wait(self, raise_if_error):
        if self.thread.is_alive():
            self.thread.join()
        if raise_if_error:
            self.raise_if_error()

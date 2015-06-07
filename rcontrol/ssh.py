import paramiko
from rcontrol.streamreader import StreamsReader
from rcontrol.core import StreamReadersExec, BaseSession


class ChannelReader(StreamsReader):
    """
    Specialized reader for paramiko.channel.Channel.
    """
    def _create_readers(self, queue, channel):
        stdout_reader = self._create_stream_reader(channel.makefile('r'),
                                                   queue,
                                                   self.stdout_callback)
        stderr_reader = None
        if not channel.combine_stderr:
            stderr_reader = \
                self._create_stream_reader(channel.makefile_stderr('r'),
                                           queue,
                                           self.stderr_callback)
        return stdout_reader, stderr_reader


class RemoteExec(StreamReadersExec):
    """
    Execute a remote ssh command.

    The execution starts as soon as the object is created.

    Basically extend a :class:`StreamReadersExec` to pass in a specialized
    stream reader, :class:`ChannelReader`.

    :param session: instance of the :class:`SshSession` responsible of
        this command execution
    :param command: the command to execute (a string)
    :param kwargs: list of argument passed to the base class constructor
    """
    def __init__(self, session, command, **kwargs):
        StreamReadersExec.__init__(self, session, ChannelReader, command,
                                   **kwargs)

        transport = self.session.ssh_client.get_transport()
        self._ssh_session = transport.open_session()
        self._ssh_session.set_combine_stderr(self._combine_stderr)

        self._ssh_session.exec_command(command)

        self._reader.start(self._ssh_session)

    def _on_finished(self):
        if not self.timed_out():
            self._set_exit_code(self._ssh_session.recv_exit_status())
        StreamReadersExec._on_finished(self)


def ssh_client(host, username=None, password=None, **kwargs):
    """
    Create a new :class:`paramiko.SSHClient`, connect it and return the
    instance.

    This is a simple wrapper around the connect method that add some good
    defaults when using username/password to connect.
    """
    client = paramiko.SSHClient()
    if username is not None:
        kwargs['username'] = username
    if password is not None:
        kwargs['password'] = password
    if username is not None and password is not None:
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        kwargs.setdefault('look_for_keys', False)
    client.connect(host, **kwargs)
    return client


class SshSession(BaseSession):
    """
    A specialized ssh session.

    :param ssh_client: an instance of a connected :class:`paramiko.SSHClient`
    :param close_client: if True, takes ownership over the ssh_client,
        meaning that it will close it when the session is closed.
    """
    def __init__(self, ssh_client, close_client=True):
        BaseSession.__init__(self)
        self.ssh_client = ssh_client
        self.sftp = ssh_client.open_sftp()
        self.close_client = close_client

    def open(self, filename, mode='r', bufsize=-1):
        return self.sftp.open(filename, mode=mode, bufsize=bufsize)

    def execute(self, command, **kwargs):
        return RemoteExec(self, command, **kwargs)

    def close(self):
        if self.close_client:
            self.ssh_client.close()

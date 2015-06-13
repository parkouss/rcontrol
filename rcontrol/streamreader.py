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

import threading
import time
from six.moves.queue import Queue, Empty


class StreamsReader(object):
    """
    Read stdout and stderr in threads.

    There is one thread to read each output stream, and one other
    to synchronize the lines read and call the appropriate callbacks.

    :param stdout_callback: a callback function called for each line
        outputed on stdout.
    :param stderr_callback: a callback function called for each line
        outputed on stderr.
    :param finished_callback: a callback function called when we are done
        reading.
    :param timeout_callback: a callback function called when we got
        a timeout error.
    :param timeout: timeout of the command in seconds, or None for no
        timeout at all.
    :param output_timeout: a timeout for the output in seconds, or None
        for no timeout at all.
    """
    def __init__(self, stdout_callback=None, stderr_callback=None,
                 finished_callback=None, timeout_callback=None,
                 timeout=None, output_timeout=None):
        self.stdout_callback = stdout_callback or (lambda line: True)
        self.stderr_callback = stderr_callback or (lambda line: True)
        self.finished_callback = finished_callback or (lambda: True)
        self.timeout_callback = timeout_callback or (lambda: True)
        self.timeout = timeout
        self.output_timeout = output_timeout
        self.thread = None

    def start(self, *args, **kwargs):
        """
        Start to read the stream(s).
        """
        queue = Queue()
        stdout_reader, stderr_reader = \
            self._create_readers(queue, *args, **kwargs)

        self.thread = threading.Thread(target=self._read,
                                       args=(stdout_reader,
                                             stderr_reader,
                                             queue))
        self.thread.daemon = True
        self.thread.start()

    def _create_readers(self, *args, **kwargs):
        """
        Subclasses must implement this.
        """
        raise NotImplementedError

    def _create_stream_reader(self, stream, queue, callback):
        thread = threading.Thread(target=self._read_stream,
                                  args=(stream, queue, callback))
        thread.daemon = True
        thread.start()
        return thread

    def _read_stream(self, stream, queue, callback):
        while True:
            line = stream.readline()
            if not line:
                break
            queue.put((line, callback))
        stream.close()

    def _read(self, stdout_reader, stderr_reader, queue):
        start_time = time.time()
        timed_out = False
        timeout = self.timeout
        if timeout is not None:
            timeout += start_time
        output_timeout = self.output_timeout
        if output_timeout is not None:
            output_timeout += start_time

        while (stdout_reader and stdout_reader.is_alive()) or \
                (stderr_reader and stderr_reader.is_alive()):
            has_line = True
            try:
                line, callback = queue.get(True, 0.02)
            except Empty:
                has_line = False
            now = time.time()
            if not has_line:
                if output_timeout is not None and now > output_timeout:
                    timed_out = True
                    break
            else:
                if output_timeout is not None:
                    output_timeout = now + self.output_timeout
                callback(line.rstrip())
            if timeout is not None and now > timeout:
                timed_out = True
                break
        if timed_out:
            self.timeout_callback()
            return
        # process remaining lines to read
        while not queue.empty():
            line, callback = queue.get(False)
            callback(line.rstrip())
        if stdout_reader:
            stdout_reader.join()
        if stderr_reader:
            stderr_reader.join()
        if not timed_out:
            self.finished_callback()

    def is_alive(self):
        """
        Return true if the synchronizing thread is still alive.
        """
        if self.thread:
            return self.thread.is_alive()
        return False

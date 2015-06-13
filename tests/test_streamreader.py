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

from rcontrol.local import ProcessReader
from mock import Mock
import subprocess
import sys
import unittest


class TestProcessReader(unittest.TestCase):
    def run_python(self, reader, cmd, combine_stderr=False):
        stderr = subprocess.STDOUT if combine_stderr else subprocess.PIPE
        proc = subprocess.Popen([sys.executable, '-u', '-c', cmd],
                                stdout=subprocess.PIPE, stderr=stderr)
        reader.start(proc)
        return proc

    def _basic_print(self, combine_stderr=False, **kwargs):
        reader = ProcessReader(**kwargs)
        proc = self.run_python(reader, """
import sys
sys.stdout.write('stdout!\\n')
sys.stderr.write('stderr!\\n')
""", combine_stderr=combine_stderr)
        reader.thread.join()
        proc.wait()
        self.assertFalse(reader.is_alive())

    def test_report_stdout_only(self):
        data = []
        self._basic_print(stdout_callback=data.append)
        self.assertEquals(data, [b'stdout!'])

    def test_report_stderr_only(self):
        data = []
        self._basic_print(stderr_callback=data.append)
        self.assertEquals(data, [b'stderr!'])

    def test_report_stdout_stderr(self):
        out, err = [],  []
        self._basic_print(stdout_callback=out.append,
                          stderr_callback=err.append)
        self.assertEquals(err, [b'stderr!'])
        self.assertEquals(out, [b'stdout!'])

    def test_report_stderr_combined(self):
        data = []
        self._basic_print(combine_stderr=True, stdout_callback=data.append)
        self.assertEquals(sorted(data), sorted([b'stdout!', b'stderr!']))

    def test_finished_called(self):
        cb = Mock()
        self._basic_print(finished_callback=cb)
        cb.assert_called_once_with()  # finished callback

    def test_timeout(self):
        cb = Mock()
        reader = ProcessReader(timeout=0.05, timeout_callback=cb)
        proc = self.run_python(reader, """
import time
time.sleep(1)
""")
        reader.thread.join()
        proc.kill()
        cb.assert_called_once_with()  # timeout callback

    def test_read_timeout(self):
        data = []
        cb = Mock()
        reader = ProcessReader(output_timeout=0.1, timeout_callback=cb,
                               stdout_callback=data.append)
        proc = self.run_python(reader, """
import time
time.sleep(0.01)
print(2)
time.sleep(1)
print(3)
""")
        reader.thread.join()
        proc.kill()
        self.assertEquals(data, [b'2'])  # 2 has been printed, not 3
        cb.assert_called_once_with()  # timeout callback

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
import unittest

from rcontrol import local


class TestLocalSession(unittest.TestCase):
    def setUp(self):
        self.session = local.LocalSession()

    def test_run_cmd(self):
        cmd = "'%s' -c 'print(1)'" % sys.executable
        task = self.session.execute(cmd)
        task.wait()
        self.assertIsInstance(task, local.LocalExec)

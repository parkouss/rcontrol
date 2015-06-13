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


def copy_file(src_os, src, dest_os, dest, chunk_size=16384):
    with src_os.open(src, 'rb') as fr:
        with dest_os.open(dest, 'wb') as fw:
            data = fr.read(chunk_size)
            while data:
                fw.write(data)
                data = fr.read(chunk_size)

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

import posixpath


def copy_file(src_os, src, dest_os, dest, chunk_size=16384):
    with src_os.open(src, 'rb') as fr:
        with dest_os.open(dest, 'wb') as fw:
            data = fr.read(chunk_size)
            while data:
                fw.write(data)
                data = fr.read(chunk_size)


def copy_dir(src_session, src, dest_session, dest, chunk_size=16384):
    dest_session.mkdir(dest)
    src_len = len(src)
    for root, dirs, files in src_session.walk(src):
        # Normalize source current directory to be relative to the top
        scontext = root[src_len:].lstrip('/')
        # calculate the dest directory
        dcontext = posixpath.join(dest, scontext)

        # create dirs
        for dir in dirs:
            path = posixpath.join(dcontext, dir)
            dest_session.mkdir(path)

        # create files
        for file in files:
            path = posixpath.join(dcontext, file)
            spath = posixpath.join(src, scontext, file)
            copy_file(src_session, spath, dest_session, path,
                      chunk_size=chunk_size)

# This file is part of Redmill.
#
# Redmill is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Redmill is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Redmill.  If not, see <http://www.gnu.org/licenses/>.

import ctypes

def buffer(str_):
    _initialize()
    result = _buffer(_cookie, str_, len(str_))
    if result is None:
        raise Exception("Cannot guess type: {}".format(_error(_cookie)))
    return result

_buffer = None
_cookie = None
_error = None

def _initialize():
    global _cookie

    if _cookie is not None:
        return

    libmagic = ctypes.CDLL(ctypes.util.find_library("magic"))

    magic_t = ctypes.c_void_p

    magic_open = libmagic.magic_open
    magic_open.restype = magic_t
    magic_open.argtypes = [ctypes.c_int]

    magic_load = libmagic.magic_load
    magic_load.restype = magic_t
    magic_load.argtypes = [magic_t, ctypes.c_char_p]

    global _error
    _error = libmagic.magic_error
    _error.restype = ctypes.c_char_p
    _error.argtypes = [magic_t]

    _cookie = magic_open(0x000010) # MAGIC_MIME
    if _cookie is None:
        raise Exception("Cannot initialize cookie")
    if magic_load(_cookie, None):
        raise Exception("Cannot load database: {}".format(_error(_cookie)))

    global _buffer
    _buffer = libmagic.magic_buffer
    _buffer.restype = ctypes.c_char_p
    _buffer.argtypes = [magic_t, ctypes.c_void_p, ctypes.c_size_t]

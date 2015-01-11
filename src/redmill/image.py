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

import calendar
import datetime
import os
import time

import PIL.Image
import libxmp

from . import xmlns

class Image(object):
    def __init__(self, path=None):
        self._path = None
        self._title = None
        self._keywords = None
        self._thumbnail = None
        self._modified = False

        if path:
            self.path = path

    ##############
    # Properties #
    ##############

    def _get_path(self):
        return self._path

    def _set_path(self, path):
        self._path = os.path.abspath(path)
        xmp = self._read_xmp()
        self._modified = False

    def _get_thumbnail(self):
        """ Thumbnail metadata
        """

        return self._thumbnail

    def _set_thumbnail(self, value):
        if self._thumbnail != value:
            self._thumbnail = value
            self._modified = True

    def _get_modified(self):
        return self._modified

    path = property(_get_path, _set_path)
    thumbnail = property(_get_thumbnail, _set_thumbnail)
    modified = property(_get_modified)

    ###########
    # Private #
    ###########

    def _read_xmp(self):
        file_ = libxmp.XMPFiles(file_path=self.path, open_forupdate=False)

        xmp = file_.get_xmp() or libxmp.XMPMeta()

        self._thumbnail = {}
        for name in ["origin", "size", "path"]:
            property_ = "Thumb{}".format(name.capitalize())
            if xmp.does_property_exist(xmlns, property_):
                value = xmp.get_property(xmlns, property_)
                if name in ["origin", "size"]:
                    value = [int(x) for x in value.split(",")]
                self._thumbnail[name] = value

        file_.close_file()

    def _write_xmp(self):
        file_ = libxmp.XMPFiles(file_path=self._path, open_forupdate=True)
        xmp = file_.get_xmp() or libxmp.XMPMeta()

        for name in ["origin", "size", "path"]:
            property_ = "Thumb{}".format(name.capitalize())
            value = self._thumbnail.get(name)
            if value:
                if name in ["origin", "size"]:
                    value = "{},{}".format(*value)

                property_ = "Thumb{}".format(name.capitalize())
                xmp.set_property(xmlns, property_, value)

        if not file_.can_put_xmp(xmp):
            file_.close_file()
            raise Exception("Cannot save XMP")

        file_.put_xmp(xmp)
        file_.close_file()

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
    def __init__(self, path):
        self._path = None

        self._title = None
        self.keywords = None

        # Time is in seconds, UTC
        self._thumbnail = {
            "path": None, "origin": None, "size": None, "time": None}

        self.path = path

    def get_thumbnail_origin(self):
        return self._thumbnail["origin"]

    def set_thumbnail_origin(self, origin):
        origin = tuple(origin)
        if not self._thumbnail["origin"] or self._thumbnail["origin"] != origin:
            self._thumbnail["origin"] = origin
            self._thumbnail["time"] = time.gmtime()

    def get_thumbnail_size(self):
        return self._thumbnail["size"]

    def set_thumbnail_size(self, size):
        size = tuple(size)
        if not self._thumbnail["size"] or self._thumbnail["size"] != size:
            self._thumbnail["size"] = size
            self._thumbnail["time"] = time.gmtime()

    def update_thumbnail(self):
        update = False
        if not os.path.isfile(self.thumbnail_path):
            update = True
        else:
            mtime = time.gmtime(os.path.getmtime(self._thumbnail["path"]))
            update = (self._thumbnail["time"] > mtime)

        if update:
            image = PIL.Image.open(self.path)
            thumbnail = image.crop((
                self._thumbnail["origin"][0], self._thumbnail["origin"][1],
                self._thumbnail["origin"][0]+self._thumbnail["size"][0],
                self._thumbnail["origin"][1]+self._thumbnail["size"][1],
            ))
            thumbnail.save(self._thumbnail["path"])

    ##############
    # Properties #
    ##############

    def _get_path(self):
        return self._path

    def _set_path(self, path):
        self._path = os.path.abspath(path)

        self._read_xmp(path)

        filename, ext = os.path.splitext(path)
        self._thumbnail["path"] = "{}_thumb{}".format(filename, ext)

    def _get_thumbnail_path(self):
        return self._thumbnail["path"]

    path = property(_get_path, _set_path)
    thumbnail_path = property(_get_thumbnail_path)

    ###########
    # Private #
    ###########

    def _read_xmp(self, path):
        file_ = libxmp.XMPFiles(file_path=path, open_forupdate=False)

        xmp = file_.get_xmp() or libxmp.XMPMeta()

        for name in ["origin", "size", "date"]:
            property_ = "Thumb{}".format(name.capitalize())
            if xmp.does_property_exist(xmlns, property_):
                self._thumbnail[name] = xmp.get_property(xmlns, property_)

        file_.close_file()

        if self._thumbnail["origin"]:
            self._thumbnail["origin"] = [
                int(x) for x in self._thumbnail["origin"].split(",")]
        if self._thumbnail["size"]:
            self._thumbnail["size"] = [
                int(x) for x in self._thumbnail["size"].split(",")]
        if self._thumbnail["time"]:
            self._thumbnail["time"] = datetime.datetime.strptime(
                self._thumbnail["time"], "%Y-%m-%dT%H:%M:%S")

    def _write_xmp(self, path):
        file_ = libxmp.XMPFiles(file_path=path, open_forupdate=True)
        xmp = file_.get_xmp() or libxmp.XMPMeta()

        if self._thumbnail["origin"]:
            xmp.set_property(
                xmlns, "ThumbOrigin",
                "{},{}".format(*self._thumbnail["origin"]))
        if self._thumbnail["size"]:
            xmp.set_property(
                xmlns, "ThumbSize",
                "{},{}".format(*self._thumbnail["size"]))
        if self._thumbnail["time"]:
            xmp.set_property_int(
                xmlns, "ThumbTime",
                calendar.timegm(self._thumbnail["time"]))

        if not file_.can_put_xmp(xmp):
            file_.close_file()
            raise Exception("Cannot save XMP")

        file_.put_xmp(xmp)
        file_.close_file()

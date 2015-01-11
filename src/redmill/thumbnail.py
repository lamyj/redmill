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

import os
import shutil

import PIL.Image

class Thumbnail(object):
    def __init__(self, image, **kwargs):
        self._image = image

        if kwargs.get("origin") and kwargs.get("path"):
            raise Exception("Origin and path are mutually exclusive")
        if kwargs.get("size") and kwargs.get("path"):
            raise Exception("Size and path are mutually exclusive")
        if kwargs.get("origin") and not kwargs.get("size"):
            raise Exception("Size and origin must both be specified")
        elif not any(kwargs.get(x) for x in ["origin", "size", "path"]):
            raise Exception("Either origin/size or path must be specified")

        self._origin = kwargs.get("origin")
        self._size = kwargs.get("size")
        self._path = kwargs.get("path")

        self._mode = "implicit" if self._origin is not None else "explicit"
        self._modified = False

    def create(self, path):
        if self._mode == "implicit":
            thumbnail = PIL.Image.open(self._image.path).crop((
                self._origin[0], self._origin[1],
                self._origin[0]+self._size[0], self._origin[1]+self._size[1]
            ))
            thumbnail.save(path)
        elif self._mode == "explicit":
            if self._path != path:
                shutil.copy(self._path, path)
        else:
            raise NotImplementedError("Invalid mode: {}".format(self._mode))

        self._modified = False

    def _get_image(self):
        return self._image

    def _set_image(self, value):
        if self._image != value:
            self._image = value
            self._modified = True

    def _get_origin(self):
        if self._mode != "implicit":
            raise Exception("No origin available in {} mode".format(self._mode))
        return self._origin

    def _set_origin(self, value):
        if self._origin != value:
            self._origin = value
            self._mode = "implicit"
            self._path = None
            self._modified = True

    def _get_size(self):
        if self._mode != "implicit":
            raise Exception("No size available in {} mode".format(self._mode))
        return self._size

    def _set_size(self, value):
        if self._size != value:
            self._size = value
            self._mode = "implicit"
            self._path = None
            self._modified = True

    def _get_path(self):
        if self._mode != "explicit":
            raise Exception("No path available in {} mode".format(self._mode))
        return self._path

    def _set_path(self, value):
        if self._path != value:
            self._path = value
            self._mode = "explicit"
            self._origin = None
            self._size = None
            self._modified = True

    def _get_mode(self):
        return self._mode

    def _get_modified(self):
        return self._modified

    image = property(_get_image, _set_image)
    origin = property(_get_origin, _set_origin)
    size = property(_get_size, _set_size)
    path = property(_get_path, _set_path)
    mode = property(_get_mode)
    modified = property(_get_modified)

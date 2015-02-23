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

from . import Image

class Catalog(object):
    def __init__(self):
        self._id_to_path = {}
        self._keyword_to_path = {}

    def add_image(self, path):
        try:
            image = Image(path)
        except Exception, e:
            print "Cannot load {}: {}".format(path, e)

        self._id_to_path[image.id] = path
        for keyword in image.keywords:
            self._keyword_to_path.setdefault(keyword, set()).add(path)

    def remove_image(self, path):
        pass

    def get_image(self, id_):
        return self._id_to_path[id_]

    def get_images(self, keyword):
        return self._keyword_to_path[keyword]

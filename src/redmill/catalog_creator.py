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
from . import Catalog

class CatalogCreator(object):
    def __init__(self, path=None):
        self._catalog = Catalog()
        if path:
            self._create_catalog(path)

    def _get_catalog(self):
        return self._catalog

    catalog = property(_get_catalog)

    def _create_catalog(self, path):
        catalog = Catalog()
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                path = os.path.join(dirpath, filename)
                catalog.add_image(path)

        self._catalog = catalog

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

import libxmp

xml_namespace = "https://github.com/lamyj/redmill"
xml_prefix = "rm"
libxmp.XMPMeta.register_namespace(xml_namespace, xml_prefix)

from derivative import Derivative
from image import Image
import processor
from catalog import Catalog
from catalog_creator import CatalogCreator
from exporter import Exporter

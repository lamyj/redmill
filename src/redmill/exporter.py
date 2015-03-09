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

import csv
import os
import shutil

import PIL.Image

from . import CatalogCreator

class Exporter(object):
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination

    def __call__(self):
        creator = CatalogCreator(self.source)
        catalog = creator.catalog

        exported_catalog = {}

        for image in catalog.id_to_image.values():
            exported, derivatives = self._export(image)
            exported_catalog[image.id] = exported
            for id, path in derivatives.items():
                exported_catalog[id] = path

        with open(os.path.join(self.destination, "catalog.csv"), "w") as fd:
            writer = csv.DictWriter(fd, fieldnames=["id", "path"])
            writer.writeheader()
            for id_, path in exported_catalog.items():
                relative_path = path[len(self.destination)+1:]
                writer.writerow({"id": id_, "path": relative_path})

    def _export(self, image):
        dirpath = os.path.dirname(image.path)[len(self.source)+1:]
        extension = os.path.splitext(image.path)[1]

        exported = os.path.join(
            self.destination, dirpath, os.path.basename(image.path))

        if not os.path.isdir(os.path.dirname(exported)):
            os.makedirs(os.path.dirname(exported))

        shutil.copy2(image.path, exported)

        derivatives = {}
        for derivative in image.derivatives:
            derivative_image = derivative.process(PIL.Image.open(image.path))

            destination = os.path.join(
                self.destination, dirpath,
                "{}{}".format(derivative.id, extension))

            derivative_image.save(destination)

            derivatives[derivative.id] = destination

        return exported, derivatives

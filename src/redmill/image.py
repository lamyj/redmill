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

import libxmp

from . import xml_namespace, xml_prefix, Derivative

class Image(object):
    def __init__(self, path=None):
        self.id = None
        self.title = None
        self.keywords = None
        self.derivatives = []
        self._path = None

        if path:
            self.path = path

    def write_metadata(self):
        file_ = libxmp.XMPFiles(file_path=self.path, open_forupdate=True)

        bag = {"prop_value_is_array": True}
        seq = {"prop_value_is_array": True, "prop_array_is_ordered": True}

        xmp = file_.get_xmp() or libxmp.XMPMeta()

        xmp.delete_property(xml_namespace, "id")
        xmp.set_property_int(xml_namespace, "id", self.id)

        xmp.delete_property(libxmp.consts.XMP_NS_DC, "title")
        xmp.set_localized_text(
            libxmp.consts.XMP_NS_DC, "title", "x-default", "x-default",
            self.title)

        xmp.delete_property(libxmp.consts.XMP_NS_DC, "subject")
        for keyword in self.keywords:
            xmp.append_array_item(
                libxmp.consts.XMP_NS_DC, "subject", keyword, bag)

        xmp.delete_property(xml_namespace, "derivatives")
        for index, derivative in enumerate(self.derivatives):
            xmp.append_array_item(
                xml_namespace, "derivatives", None, bag,
                prop_value_is_struct=True)

            path = "derivatives[{}]".format(1+index)
            xmp.set_property(
                xml_namespace, "{}/rm:type".format(path), derivative.type)
            for operation in derivative.operations:
                xmp.append_array_item(
                    xml_namespace, "{}/rm:operations".format(path), operation,
                    seq)

        if not file_.can_put_xmp(xmp):
            file_.close_file()
            raise Exception("Cannot save XMP")

        file_.put_xmp(xmp)
        file_.close_file()

    ##############
    # Properties #
    ##############

    def _get_path(self):
        return self._path

    def _set_path(self, path):
        self._path = os.path.abspath(path)
        self._read_metadata()

    path = property(_get_path, _set_path)

    ###########
    # Private #
    ###########
    def _read_metadata(self):
        file_ = libxmp.XMPFiles(file_path=self.path, open_forupdate=False)
        xmp = file_.get_xmp() or libxmp.XMPMeta()

        self.id = None
        if xmp.does_property_exist(xml_namespace, "id"):
            self.id = xmp.get_property_int(xml_namespace, "id")

        self.title = None
        if xmp.does_property_exist(libxmp.consts.XMP_NS_DC, "title"):
            self.title = xmp.get_localized_text(
                libxmp.consts.XMP_NS_DC, "title", "", "x-default")

        self.keywords = []
        keywords_count = xmp.count_array_items(
            libxmp.consts.XMP_NS_DC, "subject")
        for keyword_index in range(keywords_count):
            keyword = xmp.get_array_item(
                libxmp.consts.XMP_NS_DC, "subject", 1+keyword_index)
            self.keywords.append(keyword)

        self.derivatives = []
        derivatives_count = xmp.count_array_items(xml_namespace, "derivatives")
        for derivative_index in range(derivatives_count):
            derivative_path = "derivatives[{}]".format(derivative_index+1)
            type_ = xmp.get_property(
                xml_namespace, "{}/{}:type".format(derivative_path, xml_prefix))

            operations_path = "{}/{}:operations".format(
                derivative_path, xml_prefix)
            operations = []
            operations_count = xmp.count_array_items(
                xml_namespace, operations_path)
            for operation_index in range(operations_count):
                path = "{}[{}]".format(operations_path, operation_index+1)
                operations.append(xmp.get_property(xml_namespace, path))

            self.derivatives.append(Derivative(type_, operations))

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

from . import processor

class Derivative(object):
    """ Derivative of an image (e.g. thumbnail or resized version).
    """

    def __init__(self, id_, type_, operations):
        """ Type must be "thumbnail" or "resize". Operations must be a list of
            (operation_type, parameters).
        """

        self.id = id_
        self.type = type_
        for type_, parameters in operations:
            if type_ not in dir(processor):
                raise NotImplementedError("Unknown operation: {}".format(type_))
        self.operations = operations

    def process(self, image):
        """ Apply the operations to given PIL.Image.
        """

        return processor.apply(self.operations, image)

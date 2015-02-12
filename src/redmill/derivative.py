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
    
    def __init__(self, type_, operations):
        """ Type must be "thumbnail" or "resize". Operations can be a string
            (e.g. "crop|35.231,4.531,41.756,55;thumbnail|118") or a list of 
            (operation_type, parameters).
        """
        
        self.type = type_
        for operation in operations:
            type_, parameters = operation.split("|")
            if type_ not in dir(processor):
                raise NotImplementedError("Unknown operation: {}".format(type_))
        self.operations = operations
    
    def process(self, image):
        """ Apply the operations to given PIL.Image.
        """
        
        return processor.apply(self.operations, image)

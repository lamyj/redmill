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

def rotate(image, degrees):
    """ Angle of rotation in degrees
    """
    
    raise NotImplementedError()

def crop(image, left, top, width, height):
    """ Left edge in %, top edge in %, width in %, height in %
    """
    
    left = _parse_value(left)/100.
    top = _parse_value(top)/100.
    width = _parse_value(width)/100.
    height = _parse_value(height)/100.
    
    new_left = int(left*float(image.size[0]))
    upper = int(top*float(image.size[1]))
    right = int((left+width)*float(image.size[0]))
    lower = int((top+height)*float(image.size[1]))
    
    return image.crop((new_left, upper, right, lower))

def scale(image, width, height=None):
    """ Target width (number of pixels or "x%"), target height, defaults to
        same as width
    """
    
    raise NotImplementedError()

def thumbnail(image, width, height=None):
    """ Target width (number of pixels or "x%"), target height, defaults to
        same as width.
    """
    
    width = int(_parse_value(width, lambda x:x*image.size[0]))
    if height:
        height = _parse_value(height, lambda x:x*image.size[1])
    else:
        height = width
    
    # FIXME: interpolation ?
    return image.resize((width, height))

def resize(image, width, height):
    """ Target width (number of pixels or "x%"), target height (number of 
        pixels or "x%").
    """
    
    raise NotImplementedError()

def apply(operations, image):
    """ Apply a list of operations to the given image.
    """
    
    result = image
    for operation, parameters in operations:
        result = globals()[operation](result, *parameters)
    return result

def _parse_value(value, function=None):
    """ Transform a string parameter to a more usable value.
    """
    
    if isinstance(value, basestring):
        if value.endswith("%"):
            value = function(float(value[:-1])/100.)
        else:
            value = float(value)
    return value

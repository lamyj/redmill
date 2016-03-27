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

import io

import PIL.Image
import redmill.magic

def rotate(image, degrees):
    """ Angle of rotation in degrees
    """

    return image.rotate(degrees, PIL.Image.BILINEAR, True)

def crop(image, left, top, width, height, *args, **kwargs):
    """ Crop the input image. Left edge, top edge, width, and height can be
        specified either as a number of pixels or as "x%"
    """

    left = int(_parse_value(left, lambda x:x*image.size[0]))
    top = int(_parse_value(top, lambda x:x*image.size[1]))
    width = int(_parse_value(width, lambda x:x*image.size[0]))
    height = int(_parse_value(height, lambda x:x*image.size[1]))

    right = left+width
    bottom = top+height

    return image.crop((left, top, right, bottom))

def resize(image, width=None, height=None):
    """ Resize the input image. Target width and target height can be specified
        either as a number of pixels or as "x%". At least one of width or height
        must be given, if only one of them is present, the original aspect ratio
        is maintained.
    """

    if width is None and height is None:
        raise Exception("Width or height must be specified")
    elif width is None:
        height = _parse_value(height, lambda x:x*image.size[1])
        width = image.size[0]*float(height)/float(image.size[1])
    elif height is None:
        width = _parse_value(width, lambda x:x*image.size[0])
        height = image.size[1]*float(width)/float(image.size[0])
    else:
        width = _parse_value(width, lambda x:x*image.size[0])
        height = _parse_value(height, lambda x:x*image.size[1])

    return image.resize((int(width), int(height)), PIL.Image.BILINEAR)

def explicit(image, data):
    """
    """

    stream = io.BytesIO(data)
    image = PIL.Image.open(stream)
    image.load()

    return image

def apply(operations, image):
    """ Apply a list of operations to the given image.
    """

    result = image
    for operation, parameters in operations:
        result = globals()[operation](result, **parameters)
    return result

def _parse_value(value, function=None):
    """ Transform a string parameter to a more usable value.
    """

    try:
        if value.endswith("%"):
            value = function(float(value[:-1])/100.)
        else:
            value = float(value)
    except Exception as e:
        pass
    return value

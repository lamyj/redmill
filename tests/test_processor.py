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
import unittest

import PIL.Image

import redmill.processor

class TestProcessor(unittest.TestCase):
    def setUp(self):
        self.image = PIL.Image.open(
            os.path.join(os.path.dirname(__file__), "image.jpg"))
        self.image.load()

    def test_rotate(self):
        rotated = redmill.processor.rotate(self.image, 90)
        for x, y in zip(rotated.size, reversed(self.image.size)):
            self.assertTrue(abs(x-y)<=1)

    def test_crop_pixels(self):
        size = (50, 60)
        cropped = redmill.processor.crop(self.image, 100, 150, *size)
        for x, y in zip(cropped.size, size):
            self.assertTrue(abs(x-y)<=1)

    def test_crop_percent(self):
        factor = (40, 50)
        cropped = redmill.processor.crop(
            self.image, 10, 20, *["{}%".format(x) for x in factor])
        for x, y, f in zip(cropped.size, self.image.size, factor):
            self.assertTrue(abs(x-int(y*f/100.))<=1)

    def test_explicit(self):
        image = self.image
        self.image = PIL.Image.new("RGB", (640, 480))
        explicit = redmill.processor.explicit(
            self.image,
            open(
                os.path.join(os.path.dirname(__file__), "image.jpg"),
                "rb").read())
        self.assertEqual(explicit, image)

if __name__ == "__main__":
    unittest.main()

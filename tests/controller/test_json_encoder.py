# encoding: utf-8

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

import json
import os
import sys
import unittest

import redmill

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database_test import DatabaseTest

class TestJSONEncoder(DatabaseTest):
    def setUp(self):
        DatabaseTest.setUp(self)

    def test_basic(self):
        json.dumps(["abc", 123], cls=redmill.controller.JSONEncoder)
    
    def test_album(self):
        album = redmill.models.Album(name=u"foo")
        json.dumps(album, cls=redmill.controller.JSONEncoder)

    def test_media(self):
        album = redmill.models.Album(name=u"Röôt album")
        self.session.add(album)
        self.session.commit()

        media = redmill.models.Media(
            name=u"Mÿ îmage", author=u"John Doe", keywords=["foo", "bar"],
            filename="My_image.jpg", parent_id=album.id)
        self.session.add(media)
        self.session.commit()

        json.dumps(media, cls=redmill.controller.JSONEncoder)

if __name__ == "__main__":
    unittest.main()

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
import redmill
import database_test

class FlaskTest(database_test.DatabaseTest):
    def setUp(self):
        database_test.DatabaseTest.setUp(self)
        self.app = redmill.app.test_client()

    def _insert_album(self, name, parent_id=None):
        album = redmill.Album(name=name, parent_id=parent_id)
        self.session.add(album)
        self.session.commit()
        return album

    def _insert_media(
            self, title, author, album_id, keywords=None, filename=None):
        media = redmill.Media(title=title, author=author, album_id=album_id)
        if keywords is not None:
            media.keywords = keywords
        if filename is not None:
            media.filename = filename

        self.session.add(media)
        self.session.commit()
        return media

    def _get_response(self, method, url, *args, **kwargs):
        response = getattr(self.app, method)(url, *args, **kwargs)

        if response.status_code/100 not in [4,5]:
            if response.data:
                data = json.loads(response.data)
            else:
                data = None
        else:
            data = response.data

        return response.status_code, response.headers, data

    def _assert_album_equal(self, album, data):
        self.assertTrue(isinstance(data, dict))
        self.assertEqual(data["type"], "Album")
        for key in album.keys():
            self.assertTrue(key in data)
            self.assertEqual(data[key], album[key])

    def _assert_media_equal(self, media, data):
        self.assertTrue(isinstance(data, dict))
        self.assertEqual(data["type"], "Media")
        for key in media.keys():
            self.assertTrue(key in data)
            self.assertEqual(data[key], media[key])

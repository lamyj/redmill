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

import base64
import json
import os
import sys
import unittest

import redmill
import redmill.views

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import flask_test

class TestMedia(flask_test.FlaskTest):
    def setUp(self):
        flask_test.FlaskTest.setUp(self)
        redmill.app.config["authenticator"] = lambda x: True
        redmill.app.debug = True

    def test_get_media(self):
        album = self._insert_album(u"Röôt album")
        media = self._insert_media(u"Foo", u"Bar", album.id)

        status, _, data = self._get_response(
            "get", "/media/{}".format(media.id),
            headers={"Accept": "application/json"})

        self.assertEqual(status, 200)
        self._assert_media_equal(
            {"title": u"Foo", "author": "Bar", "album_id": album.id}, data)

    def test_get_mising_media(self):
        status, _, _ = self._get_response(
            "get", "/media/12345", headers={"Accept": "application/json"})
        self.assertEqual(status, 404)

    def test_add_media(self):
        album = self._insert_album(u"Röôt album")

        media = {
            "title": u"Tìtlë", "author": u"John Dôe",
            "keywords": ["foo", "bar"], "filename": "foo.jpg",
            "album_id": album.id
        }

        # From https://www.flickr.com/photos/britishlibrary/11005918694/
        filename = os.path.join(os.path.dirname(__file__), "..", "image.jpg")
        content = open(filename, "rb").read()

        status, _, data = self._get_response(
            "post",
            "/media/",
            data=json.dumps(dict(content=base64.b64encode(content), **media)),
            headers={"Accept": "application/json"}
        )

        self.assertEqual(status, 201)
        self._assert_media_equal(media, data)

        status, _, data = self._get_response(
            "get",
            "/media/{}".format(data["id"]),
            headers={"Accept": "application/json"})

        self.assertEqual(status, 200)
        self._assert_media_equal(media, data)

        #response = self.app.get(
        #    "/media/{}/content".format(data["id"]),
        #    headers={"Accept": "application/json"})

        #self.assertEqual(response.status_code, 200)
        #self.assertEqual(response.headers["Content-Type"], "image/jpeg")
        #match = re.match(r".*filename=\"(.*)\"", response.headers["Content-Disposition"])
        #self.assertTrue(match is not None)
        #self.assertEqual(data["filename"], match.group(1))
        #self.assertTrue(response.data == content)

    def test_add_media_without_filename(self):
        album = self._insert_album(u"Röôt album")

        media = {
            "title": u"Tìtlë", "author": u"John Dôe",
            "keywords": ["foo", "bar"],
            "album_id": album.id
        }

        # From https://www.flickr.com/photos/britishlibrary/11005918694/
        filename = os.path.join(os.path.dirname(__file__), "..", "image.jpg")
        content = base64.b64encode(open(filename, "rb").read())

        status, _, data = self._get_response(
            "post",
            "/media/",
            data=json.dumps(dict(content=content, **media)),
            headers={"Accept": "application/json"}
        )

        self.assertEqual(status, 201)
        self._assert_media_equal(media, data)

        status, _, data = self._get_response(
            "get",
            "/media/{}".format(data["id"]),
            headers={"Accept": "application/json"})

        self.assertEqual(status, 200)
        self._assert_media_equal(media, data)

    def test_add_media_wrong_album(self):
        album = self._insert_album(u"Röôt album")

        media = {
            "title": u"Tìtlë", "author": u"John Dôe",
            "keywords": ["foo", "bar"], "filename": "foo.jpg",
            "album_id": album.id+1
        }

        # From https://www.flickr.com/photos/britishlibrary/11005918694/
        filename = os.path.join(os.path.dirname(__file__), "..", "image.jpg")
        content = base64.b64encode(open(filename, "rb").read())

        status, _, _ = self._get_response(
            "post",
            "/media/",
            data=json.dumps(dict(content=content, **media)),
            headers={"Accept": "application/json"}
        )

        self.assertEqual(status, 404)

    def test_delete_media(self):
        album = self._insert_album(u"Röôt album")
        media = self._insert_media(u"Foo", u"Bar", album.id)

        media_id_ = media.id

        status, _, data = self._get_response(
            "delete", "/media/{}".format(media_id_),
            headers={"Accept": "application/json"})

        self.assertEqual(status, 204)
        self.assertEqual(data, "")

        status, _, _ = self._get_response(
            "get", "/media/{}".format(media_id_),
            headers={"Accept": "application/json"})
        self.assertEqual(status, 404)

    def test_delete_non_existing_media(self):
        status, _, _ = self._get_response(
            "delete", "/media/{}".format(12345),
            headers={"Accept": "application/json"})

        self.assertEqual(status, 404)

    def test_modify_media_content(self):
        album = self._insert_album(u"Röôt album")

        media = {
            "title": u"Tìtlë", "author": u"John Dôe",
            "keywords": ["foo", "bar"], "filename": "foo.jpg",
            "album_id": album.id
        }

        # From https://www.flickr.com/photos/britishlibrary/11005918694/
        filename = os.path.join(os.path.dirname(__file__), "..", "image.jpg")
        content = open(filename, "rb").read()

        _, _, media = self._get_response(
            "post",
            "/media/",
            data=json.dumps(dict(content=base64.b64encode(content), **media)),
            headers={"Accept": "application/json"}
        )

        #status, _, _ = self._get_response(
        #    "put",
        #    "/media/{}/content".format(media["id"]),
        #    data=base64.b64encode("foobar")
        #)
        #self.assertEqual(status, 200)

        #response = self.app.get(
        #    "/media/{}/content".format(media["id"])
        #)

        #self.assertEqual(response.status_code, 200)
        #match = re.match(r".*filename=\"(.*)\"", response.headers["Content-Disposition"])
        #self.assertTrue(match is not None)
        #self.assertEqual(media["filename"], match.group(1))
        #self.assertTrue(response.data == "foobar")

    def test_put_media(self):
        album = self._insert_album(u"Röôt album")
        media = self._insert_media(
            u"Tìtlë", u"John Dôe", album.id, ["foo", "bar"], "foo.jpg")

        status, _, data = self._get_response(
            "put",
            "/media/{}".format(media.id),
            data=json.dumps({
                "title": u"Tîtlè modified", "author": "John Dôe",
                "keywords": ["spam", "eggs"], "filename": "foo.jpg",
                "album_id": album.id}),
            headers={"Accept": "application/json"}
        )

        modified_media = {
            "title": u"Tîtlè modified", "author": u"John Dôe",
            "keywords": ["spam", "eggs"], "filename": "foo.jpg"
        }

        self.assertEqual(status, 200)
        self._assert_media_equal(modified_media, data)

        status, _, data = self._get_response(
            "get",
            "/media/{}".format(media.id),
            headers={"Accept": "application/json"}
        )

        self.assertEqual(status, 200)
        self._assert_media_equal(modified_media, data)

if __name__ == "__main__":
    unittest.main()

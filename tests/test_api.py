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
import unittest
import redmill
import flask_test

class TestAPI(flask_test.FlaskTest):

    def test_empty(self):
        status, _, data = self._get_response("get", "/api/collection")

        self.assertEqual(status, 200)
        self.assertTrue(isinstance(data, list))
        self.assertEqual(data, [])

    def test_roots(self):
        album = self._insert_album(u"Röôt album")

        status, _, data = self._get_response("get", "/api/collection")

        self.assertEqual(status, 200)

        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 1)
        self.assertTrue(isinstance(data[0], basestring))

        status, _, data = self._get_response("get", data[0])

        self.assertEqual(status, 200)
        self._assert_album_equal(
            {"name": u"Röôt album", "parent_id": None}, data)

    def test_get_album(self):
        album = self._insert_album(u"Röôt album")

        status, _, data = self._get_response(
            "get", "/api/collection/album/{}".format(album.id))

        self.assertEqual(status, 200)
        self._assert_album_equal(
            {"name": u"Röôt album", "parent_id": None}, data)

    def test_get_mising_album(self):
        status, _, _ = self._get_response(
            "get", "/api/collection/album/12345")
        self.assertEqual(status, 404)

    def test_get_media(self):
        album = self._insert_album(u"Röôt album")
        media = self._insert_media(u"Foo", u"Bar", album.id)

        status, _, data = self._get_response(
            "get", "/api/collection/media/{}".format(media.id))

        self.assertEqual(status, 200)
        self._assert_media_equal(
            {"title": u"Foo", "author": "Bar", "album_id": album.id}, data)

    def test_get_mising_media(self):
        status, _, _ = self._get_response(
            "get", "/api/collection/media/12345")
        self.assertEqual(status, 404)

    def test_add_root_album(self):
        album = { "name": u"Röôt album" }

        status, _, data = self._get_response(
            "post",
            "/api/collection/album",
            data=json.dumps(album)
        )

        self.assertEqual(status, 201)
        self._assert_album_equal(album, data)

    def test_add_sub_album(self):
        album = self._insert_album(u"Röôt album")

        sub_album = { "name": u"Süb âlbum", "parent_id": album.id }

        status, _, data = self._get_response(
            "post",
            "/api/collection/album",
            data=json.dumps(sub_album)
        )

        self.assertEqual(status, 201)
        self._assert_album_equal(sub_album, data)

    def test_add_media(self):
        album = self._insert_album(u"Röôt album")

        media = {
            "title": u"Tìtlë", "author": u"John Dôe",
            "keywords": ["foo", "bar"], "filename": "foo.jpg",
            "album_id": album.id
        }

        status, _, data = self._get_response(
            "post",
            "/api/collection/media",
            data=json.dumps(media)
        )

        self.assertEqual(status, 201)
        self._assert_media_equal(media, data)

        status, _, data = self._get_response(
            "get",
            "/api/collection/media/{}".format(data["id"]))

        self.assertEqual(status, 200)
        self._assert_media_equal(media, data)

    def test_add_media_without_filename(self):
        album = self._insert_album(u"Röôt album")

        media = {
            "title": u"Tìtlë", "author": u"John Dôe",
            "keywords": ["foo", "bar"],
            "album_id": album.id
        }

        status, _, data = self._get_response(
            "post",
            "/api/collection/media",
            data=json.dumps(media)
        )

        self.assertEqual(status, 201)
        self._assert_media_equal(media, data)

        status, _, data = self._get_response(
            "get",
            "/api/collection/media/{}".format(data["id"]))

        self.assertEqual(status, 200)
        self._assert_media_equal(media, data)

    def test_delete_leaf_album(self):
        album = self._insert_album(u"Röôt album")
        sub_album = self._insert_album(u"Süb âlbum", album.id)

        id_ = sub_album.id

        status, _, data = self._get_response(
            "delete", "/api/collection/album/{}".format(id_))

        self.assertEqual(status, 204)
        self.assertEqual(data, None)

        status, _, _ = self._get_response(
            "get", "/api/collection/album/{}".format(id_))
        self.assertEqual(status, 404)

    def test_delete_non_leaf_album(self):
        album = self._insert_album(u"Röôt album")
        sub_album = self._insert_album(u"Süb âlbum", album.id)
        media = self._insert_media(u"Foo", u"Bar", album.id)

        id_ = album.id
        sub_id_ = sub_album.id
        media_id_ = media.id

        status, _, data = self._get_response(
            "delete", "/api/collection/album/{}".format(id_))

        self.assertEqual(status, 204)
        self.assertEqual(data, None)

        status, _, _ = self._get_response(
            "get", "/api/collection/album/{}".format(id_))
        self.assertEqual(status, 404)

        status, _, _ = self._get_response(
            "get", "/api/collection/album/{}".format(sub_id_))
        self.assertEqual(status, 404)

        status, _, _ = self._get_response(
            "get", "/api/collection/media/{}".format(media_id_))
        self.assertEqual(status, 404)

    def test_delete_non_existing_album(self):
        status, _, data = self._get_response(
            "delete", "/api/collection/album/{}".format(12345))

        self.assertEqual(status, 404)

    def test_delete_media(self):
        album = self._insert_album(u"Röôt album")
        media = self._insert_media(u"Foo", u"Bar", album.id)

        media_id_ = media.id

        status, _, data = self._get_response(
            "delete", "/api/collection/media/{}".format(media_id_))

        self.assertEqual(status, 204)
        self.assertEqual(data, None)

        status, _, _ = self._get_response(
            "get", "/api/collection/media/{}".format(media_id_))
        self.assertEqual(status, 404)

    def test_delete_non_existing_media(self):
        status, _, _ = self._get_response(
            "delete", "/api/collection/media/{}".format(12345))

        self.assertEqual(status, 404)

    def test_patch_album(self):
        album = self._insert_album(u"Röôt album")

        status, _, data = self._get_response(
            "patch",
            "/api/collection/album/{}".format(album.id),
            data=json.dumps({"name": u"Röôt album modified"})
        )

        modified_album = { "name": u"Röôt album modified", "parent_id": None }

        self.assertEqual(status, 200)
        self._assert_album_equal(modified_album, data)

        status, _, data = self._get_response(
            "get",
            "/api/collection/album/{}".format(album.id)
        )

        self.assertEqual(status, 200)
        self._assert_album_equal(modified_album, data)

    def test_patch_media(self):
        album = self._insert_album(u"Röôt album")
        media = self._insert_media(
            u"Tìtlë", u"John Dôe", album.id, ["foo", "bar"], "foo.jpg")

        status, _, data = self._get_response(
            "patch",
            "/api/collection/media/{}".format(media.id),
            data=json.dumps({
                "title": u"Tîtlè modified", "keywords": ["spam", "eggs"]})
        )

        modified_media = {
            "title": u"Tîtlè modified", "author": u"John Dôe",
            "keywords": ["spam", "eggs"], "filename": "foo.jpg"
        }

        self.assertEqual(status, 200)
        self._assert_media_equal(modified_media, data)

        status, _, data = self._get_response(
            "get",
            "/api/collection/media/{}".format(media.id)
        )

        self.assertEqual(status, 200)
        self._assert_media_equal(modified_media, data)

    def test_put_album(self):
        album = self._insert_album(u"Röôt album")

        status, _, data = self._get_response(
            "put",
            "/api/collection/album/{}".format(album.id),
            data=json.dumps({
                "name": u"Röôt album modified", "parent_id": album.parent_id
            })
        )

        modified_album = { "name": u"Röôt album modified", "parent_id": None }

        self.assertEqual(status, 200)
        self._assert_album_equal(modified_album, data)

        status, _, data = self._get_response(
            "get",
            "/api/collection/album/{}".format(album.id)
        )

        self.assertEqual(status, 200)
        self._assert_album_equal(modified_album, data)

    def test_put_media(self):
        album = self._insert_album(u"Röôt album")
        media = self._insert_media(
            u"Tìtlë", u"John Dôe", album.id, ["foo", "bar"], "foo.jpg")

        status, _, data = self._get_response(
            "put",
            "/api/collection/media/{}".format(media.id),
            data=json.dumps({
                "title": u"Tîtlè modified", "author": "John Dôe",
                "keywords": ["spam", "eggs"], "filename": "foo.jpg",
                "album_id": album.id})
        )

        modified_media = {
            "title": u"Tîtlè modified", "author": u"John Dôe",
            "keywords": ["spam", "eggs"], "filename": "foo.jpg"
        }

        self.assertEqual(status, 200)
        self._assert_media_equal(modified_media, data)

        status, _, data = self._get_response(
            "get",
            "/api/collection/media/{}".format(media.id)
        )

        self.assertEqual(status, 200)
        self._assert_media_equal(modified_media, data)

if __name__ == "__main__":
    unittest.main()

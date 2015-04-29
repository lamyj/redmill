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
import database_test

class TestAPI(database_test.DatabaseTest):

    def setUp(self):
        database_test.DatabaseTest.setUp(self)
        self.app = redmill.app.test_client()

    def test_empty(self):
        status, headers, data = self._get_response("get", "/api/collection")

        self.assertEqual(status, 200)

        self.assertTrue(isinstance(data, list))
        self.assertEqual(data, [])

    def test_roots(self):
        album = redmill.Album(name=u"Röôt album")
        self.session.add(album)
        self.session.commit()

        status, headers, data = self._get_response("get", "/api/collection")

        self.assertEqual(status, 200)

        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 1)
        self.assertTrue(isinstance(data[0], basestring))

    def test_get_album(self):
        album = redmill.Album(name=u"Röôt album")
        self.session.add(album)
        self.session.commit()

        status, headers, data = self._get_response(
            "get", "/api/collection/album/{}".format(album.id))

        self.assertEqual(status, 200)

        self.assertTrue(isinstance(data, dict))
        self.assertEqual(data["type"], "Album")
        self.assertEqual(data["name"], u"Röôt album")
        self.assertEqual(data["parent_id"], None)

    def test_get_mising_album(self):
        status, headers, data = self._get_response(
            "get", "/api/collection/album/12345")
        self.assertEqual(status, 404)

    def test_get_media(self):
        album = redmill.Album(name=u"Röôt album")
        self.session.add(album)
        self.session.commit()

        media = redmill.Media(title=u"Foo", author=u"Bar", album_id=album.id)
        self.session.add(media)
        self.session.commit()

        status, headers, data = self._get_response(
            "get", "/api/collection/media/{}".format(media.id))

        self.assertEqual(status, 200)

        self.assertTrue(isinstance(data, dict))
        self.assertEqual(data["type"], "Media")
        self.assertEqual(data["title"], "Foo")
        self.assertEqual(data["author"], "Bar")
        self.assertEqual(data["album_id"], album.id)

    def test_get_mising_media(self):
        status, headers, data = self._get_response(
            "get", "/api/collection/media/12345")
        self.assertEqual(status, 404)

    def test_add_root_album(self):
        status, headers, data = self._get_response(
            "post",
            "/api/collection/album",
            data=json.dumps({"name": u"Röôt album"})
        )

        self.assertEqual(status, 201)

        self.assertTrue(isinstance(data, dict))
        self.assertEqual(data["type"], "Album")
        self.assertEqual(data["name"], u"Röôt album")
        self.assertEqual(data["parent_id"], None)

    def test_add_sub_album(self):
        album = redmill.Album(name=u"Röôt album")
        self.session.add(album)
        self.session.commit()

        status, headers, data = self._get_response(
            "post",
            "/api/collection/album",
            data=json.dumps({"name": u"Süb âlbum", "parent_id": album.id})
        )

        self.assertEqual(status, 201)

        self.assertTrue(isinstance(data, dict))
        self.assertEqual(data["type"], "Album")
        self.assertEqual(data["name"], u"Süb âlbum")
        self.assertEqual(data["parent_id"], album.id)

    def test_add_media(self):
        album = redmill.Album(name=u"Röôt album")
        self.session.add(album)
        self.session.commit()

        status, headers, data = self._get_response(
            "post",
            "/api/collection/media",
            data=json.dumps({
                "title": u"Tìtlë", "author": u"John Dôe",
                "keywords": ["foo", "bar"], "filename": "foo.jpg",
                "album_id": album.id
            })
        )

        self.assertEqual(status, 201)

        self.assertTrue(isinstance(data, dict))
        self.assertEqual(data["type"], "Media")
        self.assertEqual(data["title"], u"Tìtlë")
        self.assertEqual(data["author"], u"John Dôe")
        self.assertEqual(data["keywords"], ["foo", "bar"])
        self.assertEqual(data["filename"], "foo.jpg")
        self.assertEqual(data["album_id"], album.id)

    def test_add_media_without_filename(self):
        album = redmill.Album(name=u"Röôt album")
        self.session.add(album)
        self.session.commit()

        status, headers, data = self._get_response(
            "post",
            "/api/collection/media",
            data=json.dumps({
                "title": u"Tìtlë", "author": u"John Dôe",
                "keywords": ["foo", "bar"],
                "album_id": album.id
            })
        )

        self.assertEqual(status, 201)

        self.assertTrue(isinstance(data, dict))
        self.assertEqual(data["type"], "Media")
        self.assertEqual(data["title"], u"Tìtlë")
        self.assertEqual(data["author"], u"John Dôe")
        self.assertEqual(data["keywords"], ["foo", "bar"])
        self.assertEqual(data["filename"], "Title")
        self.assertEqual(data["album_id"], album.id)

    def test_delete_leaf_album(self):
        album = redmill.Album(name=u"Röôt album")
        self.session.add(album)
        self.session.commit()

        sub_album = redmill.Album(name=u"Süb âlbum", parent_id=album.id)
        self.session.add(sub_album)
        self.session.commit()

        id_ = sub_album.id

        status, headers, data = self._get_response(
            "delete", "/api/collection/album/{}".format(id_))

        self.assertEqual(status, 204)
        self.assertEqual(data, None)

        status, headers, data = self._get_response(
            "get", "/api/collection/album/{}".format(id_))
        self.assertEqual(status, 404)

    def test_delete_non_leaf_album(self):
        album = redmill.Album(name=u"Röôt album")
        self.session.add(album)
        self.session.commit()

        sub_album = redmill.Album(name=u"Süb âlbum", parent_id=album.id)
        self.session.add(sub_album)
        self.session.commit()

        media = redmill.Media(title=u"Foo", author=u"Bar", album_id=album.id)
        self.session.add(media)
        self.session.commit()

        id_ = album.id
        sub_id_ = sub_album.id
        media_id_ = media.id

        status, headers, data = self._get_response(
            "delete", "/api/collection/album/{}".format(id_))

        self.assertEqual(status, 204)
        self.assertEqual(data, None)

        status, headers, data = self._get_response(
            "get", "/api/collection/album/{}".format(id_))
        self.assertEqual(status, 404)

        status, headers, data = self._get_response(
            "get", "/api/collection/album/{}".format(sub_id_))
        self.assertEqual(status, 404)

        status, headers, data = self._get_response(
            "get", "/api/collection/media/{}".format(media_id_))
        self.assertEqual(status, 404)

    def test_delete_non_existing_album(self):
        status, headers, data = self._get_response(
            "delete", "/api/collection/album/{}".format(12345))

        self.assertEqual(status, 404)

    def test_delete_media(self):
        album = redmill.Album(name=u"Röôt album")
        self.session.add(album)
        self.session.commit()

        media = redmill.Media(title=u"Foo", author=u"Bar", album_id=album.id)
        self.session.add(media)
        self.session.commit()

        media_id_ = media.id

        status, headers, data = self._get_response(
            "delete", "/api/collection/media/{}".format(media_id_))

        self.assertEqual(status, 204)
        self.assertEqual(data, None)

        status, headers, data = self._get_response(
            "get", "/api/collection/media/{}".format(media_id_))
        self.assertEqual(status, 404)

    def test_delete_non_existing_media(self):
        status, headers, data = self._get_response(
            "delete", "/api/collection/media/{}".format(12345))

        self.assertEqual(status, 404)

    def test_patch_album(self):
        album = redmill.Album(name=u"Röôt album")
        self.session.add(album)
        self.session.commit()

        status, headers, data = self._get_response(
            "patch",
            "/api/collection/album/{}".format(album.id),
            data=json.dumps({"name": u"Röôt album modified"})
        )

        self.assertEqual(status, 200)

        self.assertTrue(isinstance(data, dict))
        self.assertEqual(data["type"], "Album")
        self.assertEqual(data["name"], u"Röôt album modified")
        self.assertEqual(data["parent_id"], None)

        status, headers, data = self._get_response(
            "get",
            "/api/collection/album/{}".format(album.id)
        )

        self.assertEqual(status, 200)

        self.assertTrue(isinstance(data, dict))
        self.assertEqual(data["type"], "Album")
        self.assertEqual(data["name"], u"Röôt album modified")
        self.assertEqual(data["parent_id"], None)

    def test_patch_media(self):
        album = redmill.Album(name=u"Röôt album")
        self.session.add(album)
        self.session.commit()

        media = redmill.Media(
            title=u"Tìtlë", author=u"John Dôe",
            keywords=["foo", "bar"], filename="foo.jpg",
            album_id=album.id)
        self.session.add(media)
        self.session.commit()

        status, headers, data = self._get_response(
            "patch",
            "/api/collection/media/{}".format(media.id),
            data=json.dumps({
                "title": u"Tîtlè modified", "keywords": ["spam", "eggs"]})
        )

        self.assertEqual(status, 200)

        self.assertTrue(isinstance(data, dict))
        self.assertEqual(data["type"], "Media")
        self.assertEqual(data["title"], u"Tîtlè modified")
        self.assertEqual(data["keywords"], ["spam", "eggs"])

        status, headers, data = self._get_response(
            "get",
            "/api/collection/media/{}".format(media.id)
        )

        self.assertEqual(status, 200)

        self.assertTrue(isinstance(data, dict))
        self.assertEqual(data["type"], "Media")
        self.assertEqual(data["title"], u"Tîtlè modified")
        self.assertEqual(data["keywords"], ["spam", "eggs"])

    def test_put_album(self):
        album = redmill.Album(name=u"Röôt album")
        self.session.add(album)
        self.session.commit()

        status, headers, data = self._get_response(
            "put",
            "/api/collection/album/{}".format(album.id),
            data=json.dumps({
                "name": u"Röôt album modified", "parent_id": album.parent_id
            })
        )

        self.assertEqual(status, 200)

        self.assertTrue(isinstance(data, dict))
        self.assertEqual(data["type"], "Album")
        self.assertEqual(data["name"], u"Röôt album modified")
        self.assertEqual(data["parent_id"], None)

        status, headers, data = self._get_response(
            "get",
            "/api/collection/album/{}".format(album.id)
        )

        self.assertEqual(status, 200)

        self.assertTrue(isinstance(data, dict))
        self.assertEqual(data["type"], "Album")
        self.assertEqual(data["name"], u"Röôt album modified")
        self.assertEqual(data["parent_id"], None)

    def test_put_media(self):
        album = redmill.Album(name=u"Röôt album")
        self.session.add(album)
        self.session.commit()

        media = redmill.Media(
            title=u"Tìtlë", author=u"John Dôe",
            keywords=["foo", "bar"], filename="foo.jpg",
            album_id=album.id)
        self.session.add(media)
        self.session.commit()

        status, headers, data = self._get_response(
            "put",
            "/api/collection/media/{}".format(media.id),
            data=json.dumps({
                "title": u"Tîtlè modified", "author": "John Dôe",
                "keywords": ["spam", "eggs"], "filename": "foo.jpg",
                "album_id": album.id})
        )

        self.assertEqual(status, 200)

        self.assertTrue(isinstance(data, dict))
        self.assertEqual(data["type"], "Media")
        self.assertEqual(data["title"], u"Tîtlè modified")
        self.assertEqual(data["keywords"], ["spam", "eggs"])

        status, headers, data = self._get_response(
            "get",
            "/api/collection/media/{}".format(media.id)
        )

        self.assertEqual(status, 200)

        self.assertTrue(isinstance(data, dict))
        self.assertEqual(data["type"], "Media")
        self.assertEqual(data["title"], u"Tîtlè modified")
        self.assertEqual(data["keywords"], ["spam", "eggs"])

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

if __name__ == "__main__":
    unittest.main()

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
import re
import unittest

import redmill

import flask_test

class TestAPI(flask_test.FlaskTest):

    def setUp(self):
        flask_test.FlaskTest.setUp(self)
        redmill.app.config["authenticator"] = lambda x: True

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

    def test_page_size(self):
        albums = [
            self._insert_album(u"Röôt album {}".format(index))
            for index in range(19)
        ]

        status, _, data = self._get_response(
            "get", "/api/collection?per_page=5")

        self.assertEqual(status, 200)
        self.assertEqual(len(data), 5)

    def test_first_page(self):
        albums = [
            self._insert_album(u"Röôt album {}".format(index))
            for index in range(19)
        ]

        status, default_page_headers, default_page = self._get_response(
            "get", "/api/collection?per_page=5")
        status, page_1_headers, page_1 = self._get_response(
            "get", "/api/collection?page=1&per_page=5")

        self.assertEqual(status, 200)
        self.assertEqual(default_page, page_1)
        self.assertEqual(default_page_headers, page_1_headers)

        links = self._parse_links(default_page_headers["Link"])
        links = {parameters["rel"]: (url, parameters) for url, parameters in links}

        self.assertTrue("first" not in links)
        self.assertTrue("previous" not in links)

        self.assertTrue("next" in links)
        self.assertTrue("last" in links)

    def test_middle_page(self):
        albums = [
            self._insert_album(u"Röôt album {}".format(index))
            for index in range(19)
        ]

        status, headers, data = self._get_response(
            "get", "/api/collection?page=3&per_page=5")

        self.assertEqual(status, 200)

        links = self._parse_links(headers["Link"])
        links = {parameters["rel"]: (url, parameters) for url, parameters in links}

        self.assertTrue("first" in links)
        self.assertTrue("previous" in links)

        self.assertTrue("next" in links)
        self.assertTrue("last" in links)

    def test_last_page(self):
        albums = [
            self._insert_album(u"Röôt album {}".format(index))
            for index in range(19)
        ]

        status, headers, data = self._get_response(
            "get", "/api/collection?page=4&per_page=5")

        self.assertEqual(status, 200)

        links = self._parse_links(headers["Link"])
        links = {parameters["rel"]: (url, parameters) for url, parameters in links}

        self.assertTrue("first" in links)
        self.assertTrue("previous" in links)

        self.assertTrue("next" not in links)
        self.assertTrue("last" not in links)

    def test_invalid_pages(self):
        albums = [
            self._insert_album(u"Röôt album {}".format(index))
            for index in range(19)
        ]

        status, _, _ = self._get_response(
            "get", "/api/collection?page=foo&per_page=5")
        self.assertEqual(status, 400)

        status, _, _ = self._get_response(
            "get", "/api/collection?page=-1&per_page=5")
        self.assertEqual(status, 400)

        status, _, _ = self._get_response(
            "get", "/api/collection?page=100&per_page=5")
        self.assertEqual(status, 400)

    def test_invalid_per_page(self):
        status, _, _ = self._get_response(
            "get", "/api/collection?per_page=foo")
        self.assertEqual(status, 400)

        status, _, _ = self._get_response(
            "get", "/api/collection?per_page=0")
        self.assertEqual(status, 400)

        status, _, _ = self._get_response(
            "get", "/api/collection?per_page=1000")
        self.assertEqual(status, 400)

    def test_pages(self):
        albums = [
            self._insert_album(u"Röôt album {}".format(index))
            for index in range(19)
        ]

        page = "/api/collection?per_page=5"
        done = False
        count = 0
        seen_albums = set()
        while not done:
            status, headers, data = self._get_response("get", page)
            self.assertEqual(status, 200)

            for url in data:
                status, _, album = self._get_response("get", url)
                self.assertEqual(status, 200)
                seen_albums.add(album["id"])

            links = self._parse_links(headers["Link"])
            links = {parameters["rel"]: (url, parameters) for url, parameters in links}
            if "next" in links:
                page = links["next"][0]
            else:
                done = True

            count += 1
            if count == 4:
                done = True

        self.assertEqual(count, 4)
        self.assertEqual(set(x.id for x in albums), seen_albums)

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

    def test_get_unknown(self):
        status, _, _ = self._get_response(
            "get", "/api/collection/foobar/12345")
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

    def test_add_sub_album_wrong_parent(self):
        album = self._insert_album(u"Röôt album")

        sub_album = { "name": u"Süb âlbum", "parent_id": album.id+1 }

        status, _, _ = self._get_response(
            "post",
            "/api/collection/album",
            data=json.dumps(sub_album)
        )

        self.assertEqual(status, 404)

    def test_add_media(self):
        album = self._insert_album(u"Röôt album")

        media = {
            "title": u"Tìtlë", "author": u"John Dôe",
            "keywords": ["foo", "bar"], "filename": "foo.jpg",
            "album_id": album.id
        }

        # From https://www.flickr.com/photos/britishlibrary/11005918694/
        filename = os.path.join(os.path.dirname(__file__), "image.jpg")
        content = open(filename, "rb").read()

        status, _, data = self._get_response(
            "post",
            "/api/collection/media",
            data=json.dumps(dict(content=base64.b64encode(content), **media))
        )

        self.assertEqual(status, 201)
        self._assert_media_equal(media, data)

        status, _, data = self._get_response(
            "get",
            "/api/collection/media/{}".format(data["id"]))

        self.assertEqual(status, 200)
        self._assert_media_equal(media, data)

        response = self.app.get(
            "/api/collection/media/{}/content".format(data["id"]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "image/jpeg")
        match = re.match(r".*filename=\"(.*)\"", response.headers["Content-Disposition"])
        self.assertTrue(match is not None)
        self.assertEqual(data["filename"], match.group(1))
        self.assertTrue(response.data == content)

    def test_add_media_without_filename(self):
        album = self._insert_album(u"Röôt album")

        media = {
            "title": u"Tìtlë", "author": u"John Dôe",
            "keywords": ["foo", "bar"],
            "album_id": album.id
        }

        # From https://www.flickr.com/photos/britishlibrary/11005918694/
        filename = os.path.join(os.path.dirname(__file__), "image.jpg")
        content = base64.b64encode(open(filename, "rb").read())

        status, _, data = self._get_response(
            "post",
            "/api/collection/media",
            data=json.dumps(dict(content=content, **media))
        )

        self.assertEqual(status, 201)
        self._assert_media_equal(media, data)

        status, _, data = self._get_response(
            "get",
            "/api/collection/media/{}".format(data["id"]))

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
        filename = os.path.join(os.path.dirname(__file__), "image.jpg")
        content = base64.b64encode(open(filename, "rb").read())

        status, _, _ = self._get_response(
            "post",
            "/api/collection/media",
            data=json.dumps(dict(content=content, **media))
        )

        self.assertEqual(status, 404)

    def test_delete_leaf_album(self):
        album = self._insert_album(u"Röôt album")
        sub_album = self._insert_album(u"Süb âlbum", album.id)

        id_ = sub_album.id

        status, _, data = self._get_response(
            "delete", "/api/collection/album/{}".format(id_))

        self.assertEqual(status, 204)
        self.assertEqual(data, "")

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
        self.assertEqual(data, "")

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
        self.assertEqual(data, "")

        status, _, _ = self._get_response(
            "get", "/api/collection/media/{}".format(media_id_))
        self.assertEqual(status, 404)

    def test_delete_non_existing_media(self):
        status, _, _ = self._get_response(
            "delete", "/api/collection/media/{}".format(12345))

        self.assertEqual(status, 404)

    def test_delete_unknown(self):
        status, _, _ = self._get_response(
            "delete", "/api/collection/foobar/12345")
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

    def test_modify_media_content(self):
        album = self._insert_album(u"Röôt album")

        media = {
            "title": u"Tìtlë", "author": u"John Dôe",
            "keywords": ["foo", "bar"], "filename": "foo.jpg",
            "album_id": album.id
        }

        # From https://www.flickr.com/photos/britishlibrary/11005918694/
        filename = os.path.join(os.path.dirname(__file__), "image.jpg")
        content = open(filename, "rb").read()

        _, _, media = self._get_response(
            "post",
            "/api/collection/media",
            data=json.dumps(dict(content=base64.b64encode(content), **media))
        )

        status, _, _ = self._get_response(
            "put",
            "/api/collection/media/{}/content".format(media["id"]),
            data=base64.b64encode("foobar")
        )
        self.assertEqual(status, 200)

        response = self.app.get(
            "/api/collection/media/{}/content".format(media["id"])
        )

        self.assertEqual(response.status_code, 200)
        match = re.match(r".*filename=\"(.*)\"", response.headers["Content-Disposition"])
        self.assertTrue(match is not None)
        self.assertEqual(media["filename"], match.group(1))
        self.assertTrue(response.data == "foobar")

    def test_patch_wrong_album(self):
        album = self._insert_album(u"Röôt album")

        status, _, _ = self._get_response(
            "patch",
            "/api/collection/album/{}".format(album.id+1),
            data=json.dumps({"name": u"Röôt album modified"})
        )

        self.assertEqual(status, 404)

    def test_patch_wrong_field(self):
        album = self._insert_album(u"Röôt album")

        status, _, _ = self._get_response(
            "patch",
            "/api/collection/album/{}".format(album.id),
            data=json.dumps({"foobar": u"Röôt album modified"})
        )

        self.assertEqual(status, 400)

    def test_patch_unknown(self):
        status, _, _ = self._get_response(
            "patch",
            "/api/collection/foobar/12345",
            data=json.dumps({"name": u"Röôt album modified"})
        )

        self.assertEqual(status, 404)

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

    def test_put_album_missing_field(self):
        album = self._insert_album(u"Röôt album")

        status, _, _ = self._get_response(
            "put",
            "/api/collection/album/{}".format(album.id),
            data=json.dumps({
                "parent_id": album.parent_id
            })
        )

        self.assertEqual(status, 400)

if __name__ == "__main__":
    unittest.main()

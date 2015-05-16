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
import redmill.views

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import flask_test

class TestAlbum(flask_test.FlaskTest):
    def setUp(self):
        flask_test.FlaskTest.setUp(self)
        redmill.controller.app.config["authenticator"] = lambda x: True
        redmill.controller.app.debug = True

    def test_empty(self):
        status, _, data = self._get_response(
            "get", "/albums/", headers={"Accept": "application/json"})

        self.assertEqual(status, 200)
        self.assertTrue(isinstance(data, list))
        self.assertEqual(data, [])

    def test_roots(self):
        album = self._insert_album(u"Röôt album")

        status, _, data = self._get_response(
            "get", "/albums/", headers={"Accept": "application/json"})

        self.assertEqual(status, 200)

        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 1)
        self.assertTrue(isinstance(data[0], basestring))

        status, _, data = self._get_response(
            "get", data[0], headers={"Accept": "application/json"})

        self.assertEqual(status, 200)
        self._assert_album_equal(
            {"name": u"Röôt album", "parent_id": None}, data)

    def test_get_album(self):
        album = self._insert_album(u"Röôt album")

        status, _, data = self._get_response(
            "get", "/albums/{}".format(album.id),
            headers={"Accept": "application/json"})

        self.assertEqual(status, 200)
        self._assert_album_equal(
            {"name": u"Röôt album", "parent_id": None}, data)

    def test_get_mising_album(self):
        status, _, _ = self._get_response(
            "get", "/albums/12345", headers={"Accept": "application/json"})
        self.assertEqual(status, 404)

    def test_add_root_album(self):
        album = { "name": u"Röôt album" }

        status, _, data = self._get_response(
            "post",
            "/albums/",
            data=json.dumps(album), headers={"Accept": "application/json"}
        )

        self.assertEqual(status, 201)
        self._assert_album_equal(album, data)

    def test_add_sub_album(self):
        album = self._insert_album(u"Röôt album")

        sub_album = { "name": u"Süb âlbum", "parent_id": album.id }

        status, _, data = self._get_response(
            "post",
            "/albums/",
            data=json.dumps(sub_album), headers={"Accept": "application/json"}
        )

        self.assertEqual(status, 201)
        self._assert_album_equal(sub_album, data)

    def test_add_sub_album_wrong_parent(self):
        album = self._insert_album(u"Röôt album")

        sub_album = { "name": u"Süb âlbum", "parent_id": album.id+1 }

        status, _, _ = self._get_response(
            "post",
            "/albums/",
            data=json.dumps(sub_album), headers={"Accept": "application/json"}
        )

        self.assertEqual(status, 404)

    def test_delete_leaf_album(self):
        album = self._insert_album(u"Röôt album")
        sub_album = self._insert_album(u"Süb âlbum", album.id)

        id_ = sub_album.id

        status, _, data = self._get_response(
            "delete", "/albums/{}".format(id_),
            headers={"Accept": "application/json"})

        self.assertEqual(status, 204)
        self.assertEqual(data, "")

        status, _, _ = self._get_response(
            "get", "/albums/{}".format(id_))
        self.assertEqual(status, 404)

    def test_delete_non_leaf_album(self):
        album = self._insert_album(u"Röôt album")
        sub_album = self._insert_album(u"Süb âlbum", album.id)
        media = self._insert_media(u"Foo", u"Bar", album.id)

        id_ = album.id
        sub_id_ = sub_album.id
        media_id_ = media.id

        status, _, data = self._get_response(
            "delete", "/albums/{}".format(id_),
            headers={"Accept": "application/json"})

        self.assertEqual(status, 204)
        self.assertEqual(data, "")

        status, _, _ = self._get_response(
            "get", "/albums/{}".format(id_),
            headers={"Accept": "application/json"})
        self.assertEqual(status, 404)

        status, _, _ = self._get_response(
            "get", "/albums/{}".format(sub_id_),
            headers={"Accept": "application/json"})
        self.assertEqual(status, 404)

        status, _, _ = self._get_response(
            "get", "/api/collection/media/{}".format(media_id_))
        self.assertEqual(status, 404)

    def test_delete_non_existing_album(self):
        status, _, data = self._get_response(
            "delete", "/albums/{}".format(12345),
            headers={"Accept": "application/json"})

        self.assertEqual(status, 404)

    def test_patch_album(self):
        album = self._insert_album(u"Röôt album")

        status, _, data = self._get_response(
            "patch",
            "/albums/{}".format(album.id),
            data=json.dumps({"name": u"Röôt album modified"}),
            headers={"Accept": "application/json"}
        )

        modified_album = { "name": u"Röôt album modified", "parent_id": None }

        self.assertEqual(status, 200)
        self._assert_album_equal(modified_album, data)

        status, _, data = self._get_response(
            "get",
            "/albums/{}".format(album.id),
            headers={"Accept": "application/json"}
        )

        self.assertEqual(status, 200)
        self._assert_album_equal(modified_album, data)

    def test_patch_wrong_album(self):
        album = self._insert_album(u"Röôt album")

        status, _, _ = self._get_response(
            "patch",
            "/albums/{}".format(album.id+1),
            data=json.dumps({"name": u"Röôt album modified"}),
            headers={"Accept": "application/json"}
        )

        self.assertEqual(status, 404)

    def test_patch_wrong_field(self):
        album = self._insert_album(u"Röôt album")

        status, _, _ = self._get_response(
            "patch",
            "/albums/{}".format(album.id),
            data=json.dumps({"foobar": u"Röôt album modified"}),
            headers={"Accept": "application/json"}
        )

        self.assertEqual(status, 400)

    def test_put_album(self):
        album = self._insert_album(u"Röôt album")

        status, _, data = self._get_response(
            "put",
            "/albums/{}".format(album.id),
            data=json.dumps({
                "name": u"Röôt album modified", "parent_id": album.parent_id
            }),
            headers={"Accept": "application/json"}
        )

        modified_album = { "name": u"Röôt album modified", "parent_id": None }

        self.assertEqual(status, 200)
        self._assert_album_equal(modified_album, data)

        status, _, data = self._get_response(
            "get",
            "/albums/{}".format(album.id),
            headers={"Accept": "application/json"}
        )

        self.assertEqual(status, 200)
        self._assert_album_equal(modified_album, data)

    def test_put_album_missing_field(self):
        album = self._insert_album(u"Röôt album")

        status, _, _ = self._get_response(
            "put",
            "/albums/{}".format(album.id),
            data=json.dumps({
                "parent_id": album.parent_id
            }),
            headers={"Accept": "application/json"}
        )

        self.assertEqual(status, 400)

    def test_page_size(self):
        albums = [
            self._insert_album(u"Röôt album {}".format(index))
            for index in range(19)
        ]

        status, _, data = self._get_response(
            "get", "/albums/?per_page=5",
            headers={"Accept": "application/json"})

        self.assertEqual(status, 200)
        self.assertEqual(len(data), 5)

    def test_first_page(self):
        albums = [
            self._insert_album(u"Röôt album {}".format(index))
            for index in range(19)
        ]

        status, default_page_headers, default_page = self._get_response(
            "get", "/albums/?per_page=5",
            headers={"Accept": "application/json"})
        status, page_1_headers, page_1 = self._get_response(
            "get", "/albums/?page=1&per_page=5",
            headers={"Accept": "application/json"})

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
            "get", "/albums/?page=3&per_page=5",
            headers={"Accept": "application/json"})

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
            "get", "/albums/?page=4&per_page=5",
            headers={"Accept": "application/json"})

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
            "get", "/albums/?page=foo&per_page=5",
            headers={"Accept": "application/json"})
        self.assertEqual(status, 400)

        status, _, _ = self._get_response(
            "get", "/albums/?page=-1&per_page=5",
            headers={"Accept": "application/json"})
        self.assertEqual(status, 400)

        status, _, _ = self._get_response(
            "get", "/albums/?page=100&per_page=5",
            headers={"Accept": "application/json"})
        self.assertEqual(status, 400)

    def test_invalid_per_page(self):
        status, _, _ = self._get_response(
            "get", "/albums/?per_page=foo",
            headers={"Accept": "application/json"})
        self.assertEqual(status, 400)

        status, _, _ = self._get_response(
            "get", "/albums/?per_page=0",
            headers={"Accept": "application/json"})
        self.assertEqual(status, 400)

        status, _, _ = self._get_response(
            "get", "/albums/?per_page=1000",
            headers={"Accept": "application/json"})
        self.assertEqual(status, 400)

    def test_pages(self):
        albums = [
            self._insert_album(u"Röôt album {}".format(index))
            for index in range(19)
        ]

        page = "/albums/?per_page=5"
        done = False
        count = 0
        seen_albums = set()
        while not done:
            status, headers, data = self._get_response(
                "get", page, headers={"Accept": "application/json"})
            self.assertEqual(status, 200)

            for url in data:
                status, _, album = self._get_response(
                    "get", url, headers={"Accept": "application/json"})
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

if __name__ == "__main__":
    unittest.main()

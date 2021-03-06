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

import bs4
import flask

import redmill
import redmill.models
import redmill.views

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import flask_test

try:
    unicode = unicode
except NameError:
    # 'unicode' is undefined, must be Python 3
    str = str
    unicode = str
    bytes = bytes
    basestring = (str,bytes)
else:
    # 'unicode' exists, must be Python 2
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring

class TestAlbum(flask_test.FlaskTest):
    def setUp(self):
        flask_test.FlaskTest.setUp(self)
        redmill.controller.app.config["authenticator"] = lambda x: True
        redmill.controller.app.debug = True

    def test_empty(self):
        status, _, data = self._get_response(
            "get", flask.url_for("album.get_roots"),
            headers={"Accept": "application/json"})

        self.assertEqual(status, 200)
        self.assertTrue(isinstance(data, list))
        self.assertEqual(data, [])

    def test_roots(self):
        album = self._insert_album(u"Röôt album")

        status, _, data = self._get_response(
            "get", flask.url_for("album.get_roots"),
            headers={"Accept": "application/json"})

        self.assertEqual(status, 200)

        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 1)
        self.assertTrue(isinstance(data[0], basestring))

        status, _, data = self._get_response(
            "get", data[0], headers={"Accept": "application/json"})

        self.assertEqual(status, 200)
        self._assert_album_equal(
            {"name": u"Röôt album", "parent_id": None}, data)

    def test_roots_html(self):
        album = self._insert_album(u"Röôt album")

        status, _, data = self._get_response(
            "get", flask.url_for("album.get_roots"),
            headers={"Accept": "text/html"})

        self.assertEqual(status, 200)

        document = bs4.BeautifulSoup(data)

        children = document.find_all("ul", class_="children")
        self.assertEqual(len(children), 1)
        children = children[0].find_all("a")
        self.assertEqual(len(children), 1)
        self.assertEqual(
            children[0].get("href"), flask.url_for("album.get", id_=album.id))

        name = document.find_all("input", id="name")
        self.assertEqual(len(name), 1)
        self.assertTrue(name[0].get("disabled") in ["", "disabled"])

        self.assertEqual(
            len(document.select("#metadata input[type=\"button\"]")), 0)
        self.assertEqual(
            len(document.select("#metadata input[type=\"reset\"]")), 0)

    def test_get_album(self):
        album = self._insert_album(u"Röôt album")

        status, _, data = self._get_response(
            "get", flask.url_for("album.get", id_=album.id),
            headers={"Accept": "application/json"})

        self.assertEqual(status, 200)
        self._assert_album_equal(
            {"name": u"Röôt album", "parent_id": None}, data)

    def test_get_album_html(self):
        album = self._insert_album(u"Röôt album")
        sub_album = self._insert_album(u"Süb âlbum", album.id)
        media = self._insert_media(u"Foo", u"Bar", album.id)

        status, _, data = self._get_response(
            "get", flask.url_for("album.get", id_=album.id),
            headers={"Accept": "text/html"})

        self.assertEqual(status, 200)

        document = bs4.BeautifulSoup(data)

        children = document.find_all("ul", class_="children")
        self.assertEqual(len(children), 1)
        children = children[0].find_all("a")
        self.assertEqual(len(children), 2)
        self.assertEqual(
            children[0].get("href"), flask.url_for("album.get", id_=sub_album.id))
        self.assertEqual(
            children[1].get("href"), flask.url_for("media.get", id_=media.id))

        name = document.find_all("input", id="name")
        self.assertEqual(len(name), 1)
        self.assertTrue(name[0].get("disabled") is None)

        buttons = document.select("#metadata input[type=\"button\"]")
        self.assertEqual(len(buttons), 3)
        self.assertEqual(buttons[0].get("id"), "submit")
        self.assertEqual(buttons[1].get("id"), "move")
        self.assertEqual(buttons[2].get("id"), "archive")

        self.assertEqual(len(document.find_all("input", type="reset")), 1)

    def test_get_archived_album(self):
        album = self._insert_album(u"Röôt album")

        album.status = "archived"
        self.session.commit()

        status, _, data = self._get_response(
            "get", flask.url_for("album.get", id_=album.id),
            headers={"Accept": "application/json"})

        self.assertEqual(status, 200)
        self._assert_album_equal(
            {"name": u"Röôt album", "parent_id": None}, data)

    def test_get_album_archived_parent(self):
        album = self._insert_album(u"Röôt album")
        sub_album = self._insert_album(u"Süb âlbum", album.id)

        album.status = "archived"
        self.session.commit()

        status, _, data = self._get_response(
            "get", flask.url_for("album.get", id_=sub_album.id),
            headers={"Accept": "application/json"})

        self.assertEqual(status, 200)
        self._assert_album_equal(
            {"name": u"Süb âlbum", "parent_id": album.id}, data)

    def test_get_album_archived_children(self):
        album = self._insert_album(u"Röôt album")
        sub_album = self._insert_album(u"Süb âlbum", album.id)

        sub_album.status = "archived"
        self.session.commit()

        status, _, data = self._get_response(
            "get", flask.url_for("album.get", id_=album.id),
            headers={"Accept": "application/json"})

        self.assertEqual(status, 200)
        self._assert_album_equal(
            {"name": u"Röôt album", "parent_id": None, "children": []}, data)

        status, _, data = self._get_response(
            "get", flask.url_for("album.get", id_=album.id, children="archived"),
            headers={"Accept": "application/json"})

        self.assertEqual(status, 200)
        self._assert_album_equal(
            {"name": u"Röôt album", "parent_id": None,
                "children": [flask.url_for("album.get", id_=sub_album.id)]
            }, data)

    def test_get_archived_album_not_authenticated(self):
        album = self._insert_album(u"Röôt album")

        album.status = "archived"
        self.session.commit()

        redmill.controller.app.config["authenticator"] = lambda x: False

        status, _, data = self._get_response(
            "get", flask.url_for("album.get", id_=album.id),
            headers={"Accept": "application/json"})

        self.assertEqual(status, 404)

    def test_get_archived_album_html(self):
        album = self._insert_album(u"Röôt album")
        album.status = "archived"
        self.session.commit()

        status, _, data = self._get_response(
            "get", flask.url_for("album.get", id_=album.id),
            headers={"Accept": "text/html"})

        self.assertEqual(status, 200)

        document = bs4.BeautifulSoup(data)

        name = document.find_all("input", id="name")
        self.assertEqual(len(name), 1)
        self.assertTrue(name[0].get("disabled"))

        buttons = document.select("#metadata input[type=\"button\"]")
        self.assertEqual(len(buttons), 2)
        self.assertEqual(buttons[0].get("id"), "archive")
        self.assertEqual(buttons[1].get("id"), "delete")

        self.assertEqual(len(document.find_all("input", type="reset")), 0)


    def test_get_mising_album(self):
        status, _, _ = self._get_response(
            "get", flask.url_for("album.get", id_=12345),
            headers={"Accept": "application/json"})
        self.assertEqual(status, 404)

    def test_add_root_album(self):
        album = { "name": u"Röôt album" }

        status, headers, data = self._get_response(
            "post",
            flask.url_for("album.post"),
            data=json.dumps(album), headers={"Accept": "application/json"}
        )

        self.assertEqual(status, 201)
        self._assert_album_equal(album, data)

        self.assertTrue("Location" in headers)
        status, _, data = self._get_response(
            "get", headers["Location"], headers={"Accept": "application/json"})
        self.assertEqual(status, 200)
        self._assert_album_equal(album, data)

    def test_add_sub_album(self):
        album = self._insert_album(u"Röôt album")

        sub_album = { "name": u"Süb âlbum", "parent_id": album.id }

        status, _, data = self._get_response(
            "post",
            flask.url_for("album.post"),
            data=json.dumps(sub_album), headers={"Accept": "application/json"}
        )

        self.assertEqual(status, 201)
        self._assert_album_equal(sub_album, data)

    def test_add_sub_album_wrong_parent(self):
        album = self._insert_album(u"Röôt album")

        sub_album = { "name": u"Süb âlbum", "parent_id": album.id+1 }

        status, _, _ = self._get_response(
            "post",
            flask.url_for("album.post"),
            data=json.dumps(sub_album), headers={"Accept": "application/json"}
        )

        self.assertEqual(status, 404)

    def test_add_album_wrong_json(self):
        status, _, _ = self._get_response(
            "post",
            flask.url_for("album.post"),
            data="Xabc", headers={"Accept": "application/json"}
        )

        self.assertEqual(status, 400)

    def test_add_album_missing_field(self):
        album = { "foo": u"bar" }

        status, _, _ = self._get_response(
            "post",
            flask.url_for("album.post"),
            data=json.dumps(album), headers={"Accept": "application/json"}
        )

        self.assertEqual(status, 400)

    def test_create_form_root(self):
        status, _, data = self._get_response(
            "get",
            flask.url_for("album.create_root"),
            headers={"Accept": "text/html"}
        )

        self.assertEqual(status, 200)

        document = bs4.BeautifulSoup(data)

        children = document.find_all("ul", class_="children")
        self.assertEqual(len(children), 1)
        children = children[0].find_all("a")
        self.assertEqual(len(children), 0)

        name = document.find_all("input", id="name")
        self.assertEqual(len(name), 1)
        self.assertTrue(name[0].get("disabled") is None)

        buttons = document.select("#metadata input[type=\"button\"]")
        self.assertEqual(len(buttons), 1)
        self.assertEqual(buttons[0].get("id"), "submit")

        self.assertEqual(len(document.find_all("input", type="reset")), 0)

    def test_create_form_non_root(self):
        album = self._insert_album(u"Röôt album")

        status, _, _ = self._get_response(
            "get",
            "/albums/{}/create".format(album.id),
            headers={"Accept": "text/html"}
        )

        self.assertEqual(status, 200)

    def test_create_form_wrong(self):
        status, _, _ = self._get_response(
            "get",
            "/albums/1234/create",
            headers={"Accept": "text/html"}
        )

        self.assertEqual(status, 404)

    def test_delete_leaf_album(self):
        album = self._insert_album(u"Röôt album")
        sub_album = self._insert_album(u"Süb âlbum", album.id)

        id_ = sub_album.id

        status, _, data = self._get_response(
            "delete", flask.url_for("album.delete", id_=id_),
            headers={"Accept": "application/json"})

        self.assertEqual(status, 204)
        self.assertEqual(data.decode(), "")

        status, _, _ = self._get_response(
            "get", flask.url_for("album.get", id_=id_))
        self.assertEqual(status, 404)

    def test_delete_non_leaf_album(self):
        album = self._insert_album(u"Röôt album")
        sub_album = self._insert_album(u"Süb âlbum", album.id)
        media = self._insert_media(u"Foo", u"Bar", album.id)

        id_ = album.id
        sub_id_ = sub_album.id
        media_id_ = media.id

        status, _, data = self._get_response(
            "delete", flask.url_for("album.delete", id_=id_),
            headers={"Accept": "application/json"})

        self.assertEqual(status, 204)
        self.assertEqual(data.decode(), "")

        status, _, _ = self._get_response(
            "get", flask.url_for("album.get", id_=id_),
            headers={"Accept": "application/json"})
        self.assertEqual(status, 404)

        status, _, _ = self._get_response(
            "get", flask.url_for("album.get", id_=sub_id_),
            headers={"Accept": "application/json"})
        self.assertEqual(status, 404)

        status, _, _ = self._get_response(
            "get", flask.url_for("media.get", id_=media_id_))
        self.assertEqual(status, 404)

    def test_delete_non_existing_album(self):
        status, _, data = self._get_response(
            "delete", flask.url_for("album.delete", id_=12345),
            headers={"Accept": "application/json"})

        self.assertEqual(status, 404)

    def test_patch_album(self):
        album = self._insert_album(u"Röôt album")

        status, _, data = self._get_response(
            "patch",
            flask.url_for("album.get", id_=album.id),
            data=json.dumps({"name": u"Röôt album modified"}),
            headers={"Accept": "application/json"}
        )

        modified_album = { "name": u"Röôt album modified", "parent_id": None }

        self.assertEqual(status, 200)
        self._assert_album_equal(modified_album, data)

        status, _, data = self._get_response(
            "get",
            flask.url_for("album.get", id_=album.id),
            headers={"Accept": "application/json"}
        )

        self.assertEqual(status, 200)
        self._assert_album_equal(modified_album, data)

    def test_patch_album_wrong_json(self):
        album = self._insert_album(u"Röôt album")

        status, _, _ = self._get_response(
            "patch",
            flask.url_for("album.get", id_=album.id),
            data="Xabc", headers={"Accept": "application/json"}
        )

        self.assertEqual(status, 400)

    def test_patch_wrong_album(self):
        album = self._insert_album(u"Röôt album")

        status, _, _ = self._get_response(
            "patch",
            flask.url_for("album.patch", id_=album.id+1),
            data=json.dumps({"name": u"Röôt album modified"}),
            headers={"Accept": "application/json"}
        )

        self.assertEqual(status, 404)

    def test_patch_wrong_field(self):
        album = self._insert_album(u"Röôt album")

        status, _, _ = self._get_response(
            "patch",
            flask.url_for("album.get", id_=album.id),
            data=json.dumps({"foobar": u"Röôt album modified"}),
            headers={"Accept": "application/json"}
        )

        self.assertEqual(status, 400)

    def test_put_album(self):
        album = self._insert_album(u"Röôt album")

        status, _, data = self._get_response(
            "put",
            flask.url_for("album.get", id_=album.id),
            data=json.dumps({
                "name": u"Röôt album modified", "parent_id": album.parent_id,
                "status": "archived"
            }),
            headers={"Accept": "application/json"}
        )

        modified_album = {
            "name": u"Röôt album modified", "parent_id": None,
            "status": "archived" }

        self.assertEqual(status, 200)
        self._assert_album_equal(modified_album, data)

        status, _, data = self._get_response(
            "get",
            flask.url_for("album.get", id_=album.id),
            headers={"Accept": "application/json"}
        )

        self.assertEqual(status, 200)
        self._assert_album_equal(modified_album, data)

    def test_put_album_missing_field(self):
        album = self._insert_album(u"Röôt album")

        status, _, _ = self._get_response(
            "put",
            flask.url_for("album.get", id_=album.id),
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
            "get", flask.url_for("album.get_roots", per_page=5),
            headers={"Accept": "application/json"})

        self.assertEqual(status, 200)
        self.assertEqual(len(data), 5)

    def test_first_page(self):
        albums = [
            self._insert_album(u"Röôt album {}".format(index))
            for index in range(19)
        ]

        status, default_page_headers, default_page = self._get_response(
            "get", flask.url_for("album.get_roots", per_page=5),
            headers={"Accept": "application/json"})
        status, page_1_headers, page_1 = self._get_response(
            "get", flask.url_for("album.get_roots", page=1, per_page=5),
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
            "get", flask.url_for("album.get_roots", page=3, per_page=5),
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
            "get", flask.url_for("album.get_roots", page=4, per_page=5),
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
            "get", flask.url_for("album.get_roots", page="foo", per_page=5),
            headers={"Accept": "application/json"})
        self.assertEqual(status, 400)

        status, _, _ = self._get_response(
            "get", flask.url_for("album.get_roots", page=-1, per_page=5),
            headers={"Accept": "application/json"})
        self.assertEqual(status, 400)

        status, _, _ = self._get_response(
            "get", flask.url_for("album.get_roots", page=100, per_page=5),
            headers={"Accept": "application/json"})
        self.assertEqual(status, 400)

    def test_invalid_per_page(self):
        status, _, _ = self._get_response(
            "get", flask.url_for("album.get_roots", per_page="foo"),
            headers={"Accept": "application/json"})
        self.assertEqual(status, 400)

        status, _, _ = self._get_response(
            "get", flask.url_for("album.get_roots", per_page=0),
            headers={"Accept": "application/json"})
        self.assertEqual(status, 400)

        status, _, _ = self._get_response(
            "get", flask.url_for("album.get_roots", per_page=1000),
            headers={"Accept": "application/json"})
        self.assertEqual(status, 400)

    def test_pages(self):
        albums = [
            self._insert_album(u"Röôt album {}".format(index))
            for index in range(19)
        ]

        page = flask.url_for("album.get_roots", per_page=5)
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

    def test_order_children_non_toplevel(self):
        root = self._insert_album(u"Root")
        for index in range(0,5):
            self._insert_album(u"Album {}".format(1+index), root.id)

        reordered = [root.children[x].id for x in [1,2,0,4,3]]
        status, headers, data = self._get_response(
            "post",
            flask.url_for("album.order_children", id_=root.id),
            data=json.dumps(reordered),
            headers={"Accept": "application/json"}
        )

        # CAUTION: objects must be refreshed as they have been modified outside
        # of scope
        self.session.refresh(root)
        for child in root.children:
            self.session.refresh(child)

        self.assertEqual(status, 200)
        self.assertEqual([x.id for x in root.children], reordered)

    def test_order_children_toplevel(self):
        for index in range(0,5):
            self._insert_album(u"Album {}".format(1+index), None)

        reordered = [
            redmill.models.Album.get_toplevel().children[x].id
            for x in [1,2,0,4,3]]
        status, headers, data = self._get_response(
            "post",
            flask.url_for("album.order_children_root"),
            data=json.dumps(reordered),
            headers={"Accept": "application/json"}
        )

        self.assertEqual(status, 200)
        self.assertEqual(
            [x.id for x in redmill.models.Album.get_toplevel().children],
            reordered)

    def test_order_children_wrong_album(self):
        root = self._insert_album(u"Root")
        for index in range(0,5):
            self._insert_album(u"Album {}".format(1+index), root.id)

        reordered = [root.children[x].id for x in [1,2,0,4,3]]
        status, headers, data = self._get_response(
            "post",
            flask.url_for("album.order_children", id_=root.id+1),
            data=json.dumps(reordered),
            headers={"Accept": "application/json"}
        )

        self.assertEqual(status, 400)

    def test_order_children_missing_children(self):
        root = self._insert_album(u"Root")
        for index in range(0,5):
            self._insert_album(u"Album {}".format(1+index), root.id)

        reordered = [root.children[x].id for x in [1,2,0]]
        status, headers, data = self._get_response(
            "post",
            flask.url_for("album.order_children", id_=root.id),
            data=json.dumps(reordered),
            headers={"Accept": "application/json"}
        )

        self.assertEqual(status, 400)

    def test_order_children_wrong_type(self):
        root = self._insert_album(u"Root")
        for index in range(0,5):
            self._insert_album(u"Album {}".format(1+index), root.id)

        status, headers, data = self._get_response(
            "post",
            flask.url_for("album.order_children", id_=root.id),
            data=json.dumps("[1,2,0,4,3]"),
            headers={"Accept": "application/json"}
        )

        self.assertEqual(status, 400)

if __name__ == "__main__":
    unittest.main()

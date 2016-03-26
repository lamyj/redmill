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

class TestDerivative(flask_test.FlaskTest):
    def setUp(self):
        flask_test.FlaskTest.setUp(self)
        redmill.controller.app.config["authenticator"] = lambda x: True
        redmill.controller.app.debug = True

        self.crop = ["crop", {"left": 10, "top": 20, "width": 30, "height": 40}]

    def test_get(self):
        album = self._insert_album(u"Röôt album")
        media = self._insert_media(u"Foo", u"Bar", album.id)
        derivative = self._insert_derivative(media, [self.crop])

        status, _, data = self._get_response(
            "get", "/media/{}/derivative/{}".format(media.id, derivative.id),
            headers={"Accept": "application/json"})

        self._assert_derivative_equal(
            {"media_id": media.id, "operations": [self.crop]},
            data)

    def test_get_all(self):
        album = self._insert_album(u"Röôt album")
        media = self._insert_media(u"Foo", u"Bar", album.id)
        derivative1 = self._insert_derivative(media, [self.crop])
        derivative2 = self._insert_derivative(
            media, [["crop", {"left": 40, "top": 30, "width": 20, "height": 10}]]
        )

        status, _, data = self._get_response(
            "get", "/media/{}/derivatives".format(media.id),
            headers={"Accept": "application/json"})

        self.assertEqual(len(data), 2)

        status, _, data1 = self._get_response(
            "get", data[0], headers={"Accept": "application/json"})
        self._assert_derivative_equal(
            {"media_id": media.id, "operations": derivative1.operations},
            data1)

        status, _, data2 = self._get_response(
            "get", data[1], headers={"Accept": "application/json"})
        self._assert_derivative_equal(
            {"media_id": media.id, "operations": derivative2.operations},
            data2)

    def test_get_html(self):
        album = self._insert_album(u"Röôt album")
        media = self._insert_media(u"Foo", u"Bar", album.id)
        derivative = self._insert_derivative(media, [self.crop])

        status, _, data = self._get_response(
            "get", "/media/{}/derivative/{}".format(media.id, derivative.id),
            headers={"Accept": "text/html"})

        self.assertEqual(status, 200)

    def test_get_wrong_media(self):
        album = self._insert_album(u"Röôt album")
        media = self._insert_media(u"Foo", u"Bar", album.id)
        derivative = self._insert_derivative(media, [self.crop])

        status, _, data = self._get_response(
            "get", "/media/{}/derivative/{}".format(media.id+1, derivative.id),
            headers={"Accept": "application/json"})

        self.assertEqual(status, 404)

    def test_get_wrong_derivative(self):
        album = self._insert_album(u"Röôt album")
        media = self._insert_media(u"Foo", u"Bar", album.id)
        derivative = self._insert_derivative(media, [self.crop])

        status, _, data = self._get_response(
            "get", "/media/{}/derivative/{}".format(media.id, derivative.id+1),
            headers={"Accept": "application/json"})

        self.assertEqual(status, 404)

    def test_add(self):
        album = self._insert_album(u"Röôt album")
        media = self._insert_media(u"Foo", u"Bar", album.id)

        derivative = {
            "media_id": media.id,
            "operations": [self.crop]
        }

        status, headers, data = self._get_response(
            "post",
            "/media/{}/derivative/".format(media.id),
            data=json.dumps(derivative),
            headers={"Accept": "application/json"}
        )

        self.assertEqual(status, 201)
        self._assert_derivative_equal(derivative, data)

    def test_delete(self):
        album = self._insert_album(u"Röôt album")
        media = self._insert_media(u"Foo", u"Bar", album.id)
        derivative = self._insert_derivative(media, [self.crop])

        derivative_id = derivative.id

        status, _, data = self._get_response(
            "delete", "/media/{}/derivative/{}".format(media.id, derivative_id),
            headers={"Accept": "application/json"})

        self.assertEqual(status, 204)
        self.assertEqual(data.decode(), "")

        status, _, _ = self._get_response(
            "get", "/media/{}/derivative/{}".format(media.id, derivative_id),
            headers={"Accept": "application/json"})
        self.assertEqual(status, 404)

    def test_get_content(self):
        album = self._insert_album(u"Röôt album")

        filename = os.path.join(os.path.dirname(__file__), "..", "image.jpg")
        content = open(filename, "rb").read()
        media = self._insert_media(u"Foo", u"Bar", album.id, content=content)

        derivative = self._insert_derivative(media, [self.crop])

        status, headers, data = self._get_response(
            "get",
            "/media/{}/derivative/{}/content".format(media.id, derivative.id))

        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "image/png")

    def test_patch(self):
        pass

    def test_put(self):
        pass

if __name__ == "__main__":
    unittest.main()

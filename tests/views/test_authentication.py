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
import unittest

import flask
import itsdangerous

import redmill

import flask_test

class TestAuthentication(flask_test.FlaskTest):

    @staticmethod
    def my_authenticator(request):
        return (
            request.authorization is not None and
                request.authorization.get("username") == "scott" and
                request.authorization.get("password") == "tiger")

    @staticmethod
    @redmill.controller.app.route("/f1")
    @redmill.views.authenticate(True)
    def f1():
        return "f1"

    @staticmethod
    @redmill.controller.app.route("/f2")
    @redmill.views.authenticate()
    def f2():
        return "f2"

    def setUp(self):
        flask_test.FlaskTest.setUp(self)
        redmill.controller.app.config["authenticator"] = TestAuthentication.my_authenticator
        redmill.controller.app.debug = True

    def test_login_only(self):
        status, _, data = self._get_response(
            "get",
            "/f1",
            headers=self._get_authorization("scott", "tiger")
        )
        self.assertEqual(status, 200)
        self.assertEqual(data, "f1".encode("utf-8"))

    def test_login_only_no_authorization(self):
        status, _, _ = self._get_response(
            "get",
            "/f1",
        )
        self.assertEqual(status, 401)

    def test_login_only_wrong_authorization(self):
        status, _, _ = self._get_response(
            "get",
            "/f1",
            headers=self._get_authorization("username", "password")
        )
        self.assertEqual(status, 401)

    def test_login_only_with_token(self):
        status, _, data = self._get_token("scott", "tiger")
        self.assertEqual(status, 200)

        status, _, _ = self._get_response(
            "get",
            "/f1",
            headers=self._get_authorization(data["token"], "")
        )
        self.assertEqual(status, 401)

    def test_token_with_login(self):
        status, _, data = self._get_response(
            "get",
            "/f2",
            headers=self._get_authorization("scott", "tiger")
        )
        self.assertEqual(status, 200)
        self.assertEqual(data, "f2".encode("utf-8"))

    def test_get_token(self):
        status, headers, data = self._get_token("scott", "tiger")
        self.assertEqual(status, 200)
        self.assertTrue(data.get("token") is not None)

        status, _, data = self._get_response(
            "get",
            "/f2",
            headers=self._get_authorization(data["token"], "")
        )
        self.assertEqual(status, 200)
        self.assertEqual(data, "f2".encode("utf-8"))

    def test_token_no_authorization(self):
        status, _, _ = self._get_response(
            "get",
            "/f2",
        )
        self.assertEqual(status, 401)

    def test_token_wrong_authorization(self):
        status, _, _ = self._get_response(
            "get",
            "/f2",
            headers=self._get_authorization("username", "password")
        )
        self.assertEqual(status, 401)

    def _get_token(self, username, password):
        headers = self._get_authorization(username, password)
        headers.update({"Accept": "application/json"})
        status, headers, data = self._get_response(
            "get", "/token", headers=headers)
        return status, headers, data

    def _get_authorization(self, username, password):
        credentials = base64.b64encode(
            "{}:{}".format(username, password).encode("utf-8"))
        return {"Authorization": "Basic {}".format(credentials.decode())}

if __name__ == "__main__":
    unittest.main()

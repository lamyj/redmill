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
import re
import shutil
import tempfile

import redmill

import database_test

class FlaskTest(database_test.DatabaseTest):
    def setUp(self):
        database_test.DatabaseTest.setUp(self)
        self.app = redmill.controller.app.test_client()
        self.context = redmill.controller.app.test_request_context()
        self.context.push()
        redmill.controller.app.config["media_directory"] = tempfile.mkdtemp()
        redmill.controller.app.config["SECRET_KEY"] = "deadbeef"

    def tearDown(self):
        shutil.rmtree(redmill.controller.app.config["media_directory"])
        self.context.pop()
        database_test.DatabaseTest.tearDown(self)

    def _insert_album(self, name, parent_id=None):
        album = redmill.models.Album(name=name, parent_id=parent_id)
        self.session.add(album)
        self.session.commit()
        return album

    def _insert_media(
            self, name, author, parent_id, keywords=None, filename=None,
            content=None):
        media = redmill.models.Media(name=name, author=author, parent_id=parent_id)
        if keywords is not None:
            media.keywords = keywords
        if filename is not None:
            media.filename = filename

        self.session.add(media)
        self.session.commit()

        if content:
            filename = os.path.join(
                redmill.controller.app.config["media_directory"],
                "{}".format(media.id))
            with open(filename, "wb") as fd:
                fd.write(content)

        return media

    def _insert_derivative(self, media, operations):
        derivative = redmill.models.Derivative(media, operations)

        self.session.add(derivative)
        self.session.commit()

        return derivative

    def _get_response(self, method, url, *args, **kwargs):
        response = getattr(self.app, method)(url, *args, **kwargs)

        try:
            data = json.loads(response.data)
        except ValueError:
            data = response.data

        return response.status_code, response.headers, data

    def _parse_links(self, links):
        links = links.split(",")
        links = [re.match(r"\s*<([^>]+)>(.*)", link).groups() for link in links]
        for index, (url, parameters) in enumerate(links):
            parameters = [p for p in re.split(";\s*", parameters) if p]
            parameters = dict(
                re.match(r"([^=]+)\s*=\s*\"(.*)\"", parameter).groups()
                for parameter in parameters
            )
            links[index] = url, parameters

        return links

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

    def _assert_derivative_equal(self, derivative, data):
        self.assertTrue(isinstance(data, dict))
        for key in derivative.keys():
            self.assertTrue(key in data)
            self.assertEqual(data[key], derivative[key])

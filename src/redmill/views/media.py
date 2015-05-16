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

import flask
import flask.json

from .. import app, database, models
from . import Base

class Media(Base):

    def __init__(self):
        Base.__init__(self)

    def get(self, id_):
        session = database.Session()
        value = session.query(models.Media).get(id_)
        if value is None:
            flask.abort(404)
        else:
            if flask.request.headers.get("Accept") == "application/json":
                return flask.json.dumps(value)
            else:
                flask.abort(406)

    @Base.json_only
    @Base.authenticate
    def post(self):
        session = database.Session()

        data = json.loads(flask.request.data)
        fields = ["title", "author", "content", "album_id"]
        if any(field not in data for field in fields):
            flask.abort(400)

        content = base64.b64decode(data["content"])
        if session.query(models.Album).get(data["album_id"]) is None:
            flask.abort(404)

        arguments = {
            "title": data["title"],
            "author": data["author"],
            "album_id": data["album_id"],
        }

        if "keywords" in data:
            arguments["keywords"] = data["keywords"]
        if "filename" in data:
            arguments["filename"] = data["filename"]
        else:
            arguments["filename"] = database.get_filesystem_path(
                data["title"], content)

        try:
            media = models.Media(**arguments)
            session.add(media)
            session.commit()

            filename = os.path.join(app.config["media_directory"], "{}".format(media.id))
            with open(filename, "wb") as fd:
                fd.write(content)
        except Exception as e:
            session.rollback()
            raise

        location = flask.url_for("get_collection_item", table="media", id_=media.id)
        return flask.json.dumps(media), 201, { "Location": location }

    @Base.json_only
    @Base.authenticate
    def put(self, id_):
        return self.update(id_)

    @Base.json_only
    @Base.authenticate
    def patch(self, id_):
        return self.update(id_)

    @Base.json_only
    @Base.authenticate
    def delete(self, id_):
        session = database.Session()
        value = session.query(models.Media).get(id_)
        if value is None:
            flask.abort(404)
        else:
            session.delete(value)
            session.commit()
            return "", 204 # No content

    def update(self, id_):
        fields = ["title", "author", "keywords", "filename", "album_id"]

        data = json.loads(flask.request.data)

        session = database.Session()
        item = session.query(models.Media).get(id_)
        if item is None:
            flask.abort(404)

        for field in data:
            if field not in fields:
                flask.abort(400)

        if flask.request.method == "PUT":
            if set(data.keys()) != set(fields):
                flask.abort(400)

        for field, value in data.items():
            setattr(item, field, value)

        session.commit()

        return flask.json.dumps(item)

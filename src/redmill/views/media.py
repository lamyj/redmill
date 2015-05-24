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

from .. import database, models
from . import authenticate, jsonify, request_wants_json

def get(id_):
    session = database.Session()
    media = session.query(models.Media).get(id_)
    if media is None:
        flask.abort(404)
    else:
        if request_wants_json():
            return jsonify(media)
        else:
            filename = os.path.join(
                flask.current_app.config["media_directory"],
                "{}".format(media.id))

            if os.path.isfile(filename):
                size = os.path.getsize(filename)
                prefixes = iter(["", "k", "M", "G", "T", "P", "E", "Z"])
                while size >= 1024:
                    size /= 1024.
                    prefixes.next()

                size = "{} {}B".format(int(size), prefixes.next())
            else:
                size = "(none)"

            parameters = {
                "path": media.album.parents+[media.album, media],
                "media": media, "size": size
            }
            return flask.render_template("media.html", **parameters)

@authenticate()
def post():
    session = database.Session()

    try:
        data = json.loads(flask.request.data)
    except:
        flask.abort(400)

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
    arguments["filename"] = database.get_filesystem_path(data["title"], content)

    try:
        media = models.Media(**arguments)
        session.add(media)
        session.commit()

        filename = os.path.join(flask.current_app.config["media_directory"], "{}".format(media.id))
        with open(filename, "wb") as fd:
            fd.write(content)
    except Exception as e:
        session.rollback()
        flask.abort(500, e)

    view = __name__.split(".")[-1]
    endpoint = "{}.get".format(view)
    location = flask.url_for(endpoint, id_=media.id, _method="GET")
    return flask.json.dumps(media), 201, { "Location": location }

@authenticate()
def put(id_):
    return _update(id_)

@authenticate()
def patch(id_):
    return _update(id_)

@authenticate()
def delete(id_):
    session = database.Session()
    value = session.query(models.Media).get(id_)
    if value is None:
        flask.abort(404)
    else:
        try:
            filename = os.path.join(
                flask.current_app.config["media_directory"],
                "{}".format(value.id))
            os.remove(filename)
            session.delete(value)
        except Exception as e:
            session.rollback()
            flask.abort(500, e)
        session.commit()
        return "", 204 # No content

def _update(id_):
    fields = ["title", "author", "keywords", "album_id"]

    try:
        data = json.loads(flask.request.data)
    except:
        flask.abort(400)

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

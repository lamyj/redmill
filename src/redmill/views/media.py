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
import datetime
import json
import os

import flask
import flask.json

from .. import database, models
from . import (
    authenticate, get_item, jsonify, request_wants_json, get_children_filter,
    get_tree)

def as_html(media, parents, creation=False):
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
        "media": media, "size": size,
        "parents": [models.Album.get_toplevel()]+parents, "creation": creation,
        "tree": get_tree(media.parent.id)
    }
    return flask.render_template("media.html", **parameters)

def get(id_):
    session = database.Session()
    media = get_item(session, models.Media, id_)

    if request_wants_json():
        return jsonify(media)
    else:
        return as_html(media, media.parents)

@authenticate()
def post():
    session = database.Session()

    try:
        data = json.loads(flask.request.data)
    except:
        flask.abort(400)

    fields = ["name", "author", "content", "parent_id"]
    if any(field not in data for field in fields):
        flask.abort(400)

    content = base64.b64decode(data["content"])
    if session.query(models.Album).get(data["parent_id"]) is None:
        flask.abort(404)

    arguments = {
        "name": data["name"],
        "author": data["author"],
        "parent_id": data["parent_id"],
    }

    if "keywords" in data:
        arguments["keywords"] = data["keywords"]
    arguments["filename"] = database.get_filesystem_path(data["name"], content)

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

@authenticate()
def create(parent_id):
    session = database.Session()
    album = session.query(models.Album).get(parent_id)
    if album is None:
        flask.abort(404)

    parents = album.parents+[album]

    media = models.Media(
        id=None, parent_id=parent_id, name="", author="",
        rank=len(album.children))
    return as_html(media, parents, True)

def _update(id_):
    fields = ["name", "author", "keywords", "parent_id", "status"]

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

    item.modified_at = datetime.datetime.now()

    session.commit()

    return flask.json.dumps(item)

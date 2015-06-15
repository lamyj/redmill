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
from . import authenticate, get_item, jsonify, request_wants_json

def get(id_):
    session = database.Session()
    media = get_item(session, models.Media, id_)

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

        metadata = [
            ("name", (
                "Title: ", "input", { "type": "text", "value": media.name },
                "", False, "<br>")),
            ("author", (
                "Author: ", "input", { "type": "text", "value": media.author },
                "", False, "<br>")),
            ("keywords", (
                "Keywords: ", "input",
                {
                    "type": "text", "value": ", ".join(media.keywords or []),
                    "data-rm-type": "list"
                },
                "", False, "<br>")),
            ("created_at", (
                "Created: ", "spam", { },
                media.created_at.isoformat(), True, "<br>")),
            ("modified_at", (
                "Modified: ", "span", { },
                media.modified_at.isoformat() if media.modified_at else "",
                True, "<br>")),
            ("status", (
                "", "input", { "type": "hidden", "value": media.status },
                "", False, "")),
            ("size", ("Size: ", "span", { }, size, True, "<br>")),
        ]

        buttons = [
            ("submit", ("input", {"type": "button", "value": "Update"}, " ")),
            ("reset", ("input", {"type": "reset", "value": "Reset"}, " ")),
            ("archive", (
                "input", {
                    "type": "button",
                    "value": "Archive" if media.status != "archived" else "Restore"
                }, " ")),
        ]

        send = ["name", "author", "keywords"]

        parameters = {
            "title": u"{} - {}".format(media.name, media.parent.name),
            "path": media.parents+[media],
            "metadata": metadata, "buttons": buttons, "send": send,
            "content": flask.url_for("media_content.get", id_=media.id),
            "method": "PATCH", "url": flask.url_for("media.patch", id_=media.id)
        }
        return flask.render_template("media.html", **parameters)

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

    class Dummy(object):
        pass
    dummy = Dummy()
    dummy.id = 0
    dummy.parent_id = 0
    dummy.name = ""
    dummy.author = ""
    dummy.keywords = []

    metadata = [
        ("name", (
            "Title: ", "input", { "type": "text", "value": "" },
            "", False, "<br>")),
        ("author", (
            "Author: ", "input", { "type": "text", "value": "" },
            "", False, "<br>")),
        ("keywords", (
            "Keywords: ", "input",
            { "type": "text", "value": "", "data-rm-type": "list" },
            "", False, "<br>")),
        ("parent_id", (
            "", "input", { "type": "hidden", "value": album.id },
            "", False, "")),
    ]

    buttons = [
        ("submit", ("input", {"type": "button", "value": "Create"}, ""))
    ]

    send = ["name", "author", "keywords", "parent_id", "content"]

    parameters = {
        "title": u"{} - {}".format(u"New media", album.name),
        "path": album.parents+[album],
        "metadata": metadata, "buttons": buttons, "send": send,
        "method": "POST", "url": flask.url_for("media.post")
    }

    return flask.render_template("media.html", **parameters)

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

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

import datetime
import json
import os

import flask
import flask.json

from .. import database, models
from . import authenticate, get_item, jsonify, request_wants_json

def get_children_filter():
    children_filter = flask.request.args.get("children")
    if not children_filter:
        children_filter = ["published"]
    else:
        children_filter = children_filter.split("|")

    return children_filter

def get(id_):
    session = database.Session()
    album = get_item(session, models.Album, id_)

    parents = None
    if not request_wants_json():
        # Request parents now since we are going to expunge the album from the
        # session
        parents = album.parents

    # Avoid modifying the session: remove the album from the session before
    # filtering children
    session.expunge(album)
    album.children = [
        x for x in album.children if x.status in get_children_filter()]

    if request_wants_json():
        return jsonify(album)
    else:
        metadata = [
            ("name", (
                "Title: ", "input", { "type": "text", "value": album.name },
                "", False, "<br>")),
            ("created_at", (
                "Created: ", "spam", { },
                album.created_at.isoformat(), True, "<br>")),
            ("modified_at", (
                "Modified: ", "span", { },
                album.modified_at.isoformat() if album.modified_at else "",
                True, "<br>")),
            ("status", (
                "", "input", { "type": "hidden", "value": album.status },
                "", False, "")),
        ]

        buttons = []

        if album.status != "archived":
            buttons.extend([
                ("submit", ("input", {"type": "button", "value": "Update"}, " ")),
                ("reset", ("input", {"type": "reset", "value": "Reset"}, " ")),
            ])

        buttons.append(
            ("archive", (
                "input", {
                    "type": "button",
                    "value": "Archive" if album.status != "archived" else "Restore"
                }, " " if album.status == "archived" else ""))
        )

        if album.status == "archived":
            buttons.append(
                ("delete", ("input", {"type": "button", "value": "Delete"}, ""))
            )

        send = ["name"]

        creation_links = [
            (flask.url_for("album.create", parent_id=album.id), "New album"),
            (flask.url_for("media.create", parent_id=album.id), "New media"),
        ]

        parameters = {
            "title": u"{} - {}".format(album.name, parents[-1].name) if parents else album.name,
            "path": parents+[album],
            "metadata": metadata, "buttons": buttons, "send": send,
            "creation_links": creation_links, "children": album.children,
            "method": "PATCH", "url": flask.url_for("album.patch", id_=album.id)
        }

        if album.status == "archived":
            parameters.update({
                "delete_url": flask.url_for("album.delete", id_=album.id)
            })

        return flask.render_template("album.html", **parameters)

def get_roots():
    try:
        page = int(flask.request.args.get("page", 1))
    except ValueError as e:
        flask.abort(400)
    # Switch to 0-based indices
    page -= 1

    if page < 0:
        flask.abort(400)

    try:
        per_page = int(flask.request.args.get("per_page", 30))
    except ValueError as e:
        flask.abort(400)
    if per_page <= 0 or per_page > 100:
        flask.abort(400)

    session = database.Session()

    count = session.query(models.Album).filter_by(parent_id=None).count()

    last_page = int(count/per_page)

    # Last page is 0-based
    if page > last_page:
        flask.abort(400)

    begin = page*per_page
    end = begin+per_page
    album_list = session.query(models.Album)\
        .filter_by(parent_id=None)\
        .order_by(models.Album.id)\
        .offset(begin).limit(end-begin)

    # Filter root albums according to requested status
    album_list = [x for x in album_list if x.status in get_children_filter()]

    view = __name__.split(".")[-1]
    root_endpoint = "{}.get_roots".format(view)
    album_endpoint = "{}.get".format(view)

    # Values in links are 1-based
    links = {}
    if page > 1:
        links["previous"] = flask.url_for(
            root_endpoint, page=(page+1)-1, per_page=per_page)
        links["first"] = flask.url_for(root_endpoint, page=1, per_page=per_page)
    if page < last_page:
        links["next"] = flask.url_for(
            root_endpoint, page=(page+1)+1, per_page=per_page)
        links["last"] = flask.url_for(
            root_endpoint, page=last_page+1, per_page=per_page)

    links = ", ".join(
        "<{}>; rel=\"{}\"".format(link, type_) for type_, link in links.items())

    if request_wants_json():
        urls = [
            flask.url_for(album_endpoint, id_=album.id)
            for album in album_list
        ]
        return jsonify(urls, headers={"Link": links})
    else:
        metadata = [
            ("name", (
                "Title: ", "input",
                { "type": "text", "value": "Root album", "disabled": "disabled" },
                "", False, "<br>")),
        ]

        buttons = []
        send = []

        creation_links = [
            (flask.url_for("album.create_root"), "New album"),
        ]

        parameters = {
            "title": u"Root album",
            "path": [],
            "metadata": metadata, "buttons": buttons, "send": send,
            "creation_links": creation_links, "children": album_list,
        }

        return flask.render_template("album.html", **parameters)

@authenticate()
def post():
    try:
        data = json.loads(flask.request.data)
    except:
        flask.abort(400, "Invalid JSON")
    fields = ["name"]
    if any(field not in data for field in fields):
        flask.abort(400, "Missing field")

    parent_id = data.get("parent_id")

    session = database.Session()
    if parent_id and session.query(models.Album).get(parent_id) is None:
        flask.abort(404)

    album = models.Album(name=data["name"], parent_id=parent_id)
    session.add(album)
    session.commit()

    view = __name__.split(".")[-1]
    endpoint = "{}.get".format(view)
    location = flask.url_for(endpoint, id_=album.id, _method="GET")

    return jsonify(album, 201, headers={"Location": location})

@authenticate()
def put(id_):
    return _update(id_)

@authenticate()
def patch(id_):
    return _update(id_)

@authenticate()
def delete(id_):
    session = database.Session()
    value = session.query(models.Album).get(id_)
    if value is None:
        flask.abort(404)
    else:
        to_delete = []
        to_process = [value]
        while to_process:
            album = to_process.pop(0)
            for child in album.children:
                to_delete.insert(0, child)
                if child.type == "album":
                    to_process.insert(0, child)
        for item in to_delete:
            session.delete(item)

        session.delete(value)
        session.commit()
        return "", 204 # No content

@authenticate()
def create(parent_id=None):
    session = database.Session()
    if parent_id is not None:
        album = session.query(models.Album).get(parent_id)
        if album is None:
            flask.abort(404)
    else:
        album = None

    if album:
        path = album.parents+[album]
    else:
        path = []

    metadata = [
        ("name", (
            "Title: ", "input", { "type": "text", "value": "" },
            "", False, "<br>")),
        ("parent_id", (
            "", "input",
            { "type": "hidden", "value": flask.json.dumps(parent_id) if parent_id else "" },
            "", False, "")),
    ]

    buttons = [
        ("submit", ("input", {"type": "button", "value": "Create"}, ""))
    ]

    send = ["name", "parent_id"]

    parameters = {
        "title": u"{} - {}".format(u"New album", album.name) if parent_id else u"New root album",
        "path": path, "metadata": metadata, "buttons": buttons, "send": send,
        "children": [],
        "method": "POST", "url": flask.url_for("album.post")
    }

    return flask.render_template("album.html", **parameters)


def _update(id_):
    fields = ["name", "parent_id", "status"]

    try:
        data = json.loads(flask.request.data)
    except:
        flask.abort(400)

    session = database.Session()
    item = session.query(models.Album).get(id_)
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

    return jsonify(item)

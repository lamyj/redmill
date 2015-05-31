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
from . import authenticate, jsonify, request_wants_json

def get(id_):
    session = database.Session()
    album = session.query(models.Album).get(id_)
    if album is None:
        flask.abort(404)
    else:
        if request_wants_json():
            return jsonify(album)
        else:
            return flask.render_template(
                "album.html", album=album, path=album.parents+[album])

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
        class Dummy(object):
            pass
        dummy = Dummy()
        dummy.id = None
        dummy.name = "Root"
        dummy.children = album_list
        dummy.created_at = None
        dummy.modified_at = None
        return flask.render_template("album.html", album=dummy, path=[])

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

    return flask.render_template("create_album.html", album=album, path=path)


def _update(id_):
    fields = ["name", "parent_id"]

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

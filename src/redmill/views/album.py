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
from . import (
    authenticate, get_item, jsonify, request_wants_json, get_children_filter, get_tree)

def get_album(id_):
    """ Return the requested album (or the top-level dummy album if id_ is None)
        after filtering its children and paginating.

        Since we are filtering the children, the album must not be in the
        session and the parents are hence returned as a separate value.

        Pagination links are added as a "links" member.
    """

    session = database.Session()

    if id_ is None:
        album = models.Album.get_toplevel()
        parents = []
    else:
        album = get_item(session, models.Album, id_)
        parents = album.parents
        # Avoid modifying the session: remove the album from the session before
        # filtering children
        session.expunge(album)

    children_filter = get_children_filter()
    album.children = [
        x for x in album.children if x.status in children_filter]

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

    last_page = int(len(album.children)/per_page)

    # Last page is 0-based
    if page > last_page:
        flask.abort(400)

    begin = page*per_page
    end = begin+per_page

    album.children = album.children[begin:end]

    # Values in links are 1-based
    links = {}
    if page > 1:
        links["previous"] = flask.url_for(
            "album.get_roots", page=(page+1)-1, per_page=per_page)
        links["first"] = flask.url_for("album.get_roots", page=1, per_page=per_page)
    if page < last_page:
        links["next"] = flask.url_for(
            "album.get_roots", page=(page+1)+1, per_page=per_page)
        links["last"] = flask.url_for(
            "album.get_roots", page=last_page+1, per_page=per_page)

    album.links = links

    return album, parents

def as_html(album, parents, children_filter, creation=False):
    parameters = {
        "album": album, "parents": [models.Album.get_toplevel()] + parents,
        "children_filter": children_filter, "creation": creation,
        "tree": get_tree(album.id)
    }
    if album.id:
        parameters.update({
            "method": "PATCH",
            "url": flask.url_for("album.patch", id_=album.id)})

    return flask.render_template("album.html", **parameters)

def get(id_):
    album, parents = get_album(id_)
    if request_wants_json():
        return jsonify(album)
    else:
        return as_html(album, parents, get_children_filter())

def get_roots():
    album, parents = get_album(None)
    if request_wants_json():
        urls = [
            flask.url_for("album.get", id_=child.id)
            for child in album.children
        ]
        links = ", ".join(
            "<{}>; rel=\"{}\"".format(link, type_) for type_, link in album.links.items())
        return jsonify(urls, headers={"Link": links})
    else:
        return as_html(album, parents, get_children_filter())

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
        parent = session.query(models.Album).get(parent_id)
        if parent is None:
            flask.abort(404)
        parents = parent.parents+[parent]
    else:
        parent = models.Album.get_toplevel()
        parents = []

    album = models.Album(
        id=None, parent_id=parent_id, name="", rank=len(parent.children))
    return as_html(album, parents, ["published"], True)

@authenticate()
def order_children(id_):
    children_ids = json.loads(flask.request.data)
    if not isinstance(children_ids, (list, tuple)):
        flask.abort(400)

    session = database.Session()

    if id_ is None:
        album = models.Album.get_toplevel()
    else:
        album = get_item(session, models.Album, id_)

    album_children = [x.id for x in album.children]
    if set(album_children) != set(children_ids):
        flask.abort(400)

    for index, child_id in enumerate(children_ids):
        item = session.query(models.Item).get(child_id)
        item.rank = index

    session.commit()

    return ("", 200)

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

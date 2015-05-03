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

from .. import app, database, magic, Album, Media
from json_ import JSONEncoder

def get_table(table):
    tables = { "album": Album, "media": Media }
    return tables[table]

@app.route("/api/collection", methods=["GET"])
def get_root_collections():
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

    count = session.query(Album).filter_by(parent_id=None).count()

    last_page = int(count/per_page)

    # Last page is 0-based
    if page > last_page:
        flask.abort(400)

    begin = page*per_page
    end = begin+per_page
    album_list = session.query(Album).filter_by(parent_id=None).order_by(Album.id).all()[begin:end]

    # Values in links are 1-based
    links = {}
    if page > 1:
        links["previous"] = flask.url_for(
            "get_root_collections", page=(page+1)-1, per_page=per_page)
        links["first"] = flask.url_for(
            "get_root_collections", page=1, per_page=per_page)
    if page < last_page:
        links["next"] = flask.url_for(
            "get_root_collections", page=(page+1)+1, per_page=per_page)
        links["last"] = flask.url_for(
            "get_root_collections", page=last_page+1, per_page=per_page)

    links = ", ".join(
        "<{}>; rel=\"{}\"; foo=\"bar\"".format(link, type_) for type_, link in links.items())

    urls = [
        flask.url_for("get_collection_item", table="album", id_=album.id)
        for album in album_list
    ]
    return json.dumps(urls), 200 , {"Link": links}

@app.route("/api/collection/<table>/<id_>", methods=["GET"])
def get_collection_item(table, id_):
    try:
        table = get_table(table)
    except KeyError:
        flask.abort(404)

    session = database.Session()
    value = session.query(table).get(id_)
    if value is None:
        flask.abort(404)
    else:
        return json.dumps(value, cls=JSONEncoder)

@app.route("/api/collection/media/<id_>/content", methods=["GET"])
def get_media_content(id_):
    session = database.Session()
    media = session.query(Media).get(id_)
    if media is None:
        flask.abort(404)

    filename = os.path.join(app.media_directory, "{}".format(media.id))
    with open(filename, "rb") as fd:
        data = fd.read()

    headers = {
        "Content-Type": magic.buffer(data),
        "Content-Disposition": "inline; filename=\"{}\"".format(media.filename)
    }

    return data, 200, headers

@app.route("/api/collection/<table>/<id_>", methods=["DELETE"])
def delete_collection_item(table, id_):
    try:
        table = get_table(table)
    except KeyError:
        flask.abort(404)

    session = database.Session()
    value = session.query(table).get(id_)
    if value is None:
        flask.abort(404)
    else:
        if table == Album:
            to_delete = []
            to_process = [value]
            while to_process:
                album = to_process.pop(0)
                for child in album.media:
                    to_delete.insert(0, child)
                for child in album.children:
                    to_delete.insert(0, child)
                    to_process.insert(0, child)
            for item in to_delete:
                session.delete(item)

        session.delete(value)
        session.commit()
        return "", 204 # No content

@app.route("/api/collection/album", methods=["POST"])
def create_album():
    session = database.Session()

    data = json.loads(flask.request.data)
    fields = ["name"]
    if any(field not in data for field in fields):
        flask.abort(400)

    parent_id = data.get("parent_id")
    if parent_id and session.query(Album).get(parent_id) is None:
        flask.abort(404)

    album = Album(name=data["name"], parent_id=parent_id)
    session.add(album)
    session.commit()

    location = flask.url_for(
        "get_collection_item", table="album", id_=album.id)
    return json.dumps(album, cls=JSONEncoder), 201, { "Location": location }

@app.route("/api/collection/media", methods=["POST"])
def create_media():
    session = database.Session()

    data = json.loads(flask.request.data)
    fields = ["title", "author", "content", "album_id"]
    if any(field not in data for field in fields):
        flask.abort(400)

    content = base64.b64decode(data["content"])
    if session.query(Album).get(data["album_id"]) is None:
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
        media = Media(**arguments)
        session.add(media)
        session.commit()

        filename = os.path.join(app.media_directory, "{}".format(media.id))
        with open(filename, "wb") as fd:
            fd.write(content)
    except Exception as e:
        session.rollback()
        raise

    location = flask.url_for("get_collection_item", table="media", id_=media.id)
    return json.dumps(media, cls=JSONEncoder), 201, { "Location": location }

@app.route("/api/collection/<table>/<id_>", methods=["PATCH", "PUT"])
def update(table, id_):
    fields = {
        Album: ["name", "parent_id"],
        Media: ["title", "author", "keywords", "filename", "album_id"]
    }

    data = json.loads(flask.request.data)

    try:
        table = get_table(table)
    except KeyError:
        flask.abort(404)

    session = database.Session()
    item = session.query(table).get(id_)
    if item is None:
        flask.abort(404)

    for field in data:
        if field not in fields[type(item)]:
            flask.abort(400)

    if flask.request.method == "PUT":
        if set(data.keys()) != set(fields[type(item)]):
            flask.abort(400)

    for field, value in data.items():
        setattr(item, field, value)

    session.commit()

    return json.dumps(item, cls=JSONEncoder)

@app.route("/api/collection/media/<id_>/content", methods=["PATCH", "PUT"])
def update_media_content(id_):
    session = database.Session()
    media = session.query(Media).get(id_)
    if media is None:
        flask.abort(404)

    content = base64.b64decode(flask.request.data)

    filename = os.path.join(app.media_directory, "{}".format(media.id))
    with open(filename, "wb") as fd:
        fd.write(content)

    return "", 200

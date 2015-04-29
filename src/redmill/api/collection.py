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

import flask

from .. import app, database, Album, Media
from json_ import JSONEncoder

def get_table(table):
    tables = { "album": Album, "media": Media }
    return tables[table]

@app.route("/api/collection", methods=["GET"])
def get_root_collections():
    page = flask.request.args.get("page", 1)
    per_page = min(flask.request.args.get("per_page", 30), 100)

    begin = (page-1)*per_page
    end = begin+per_page

    session = database.Session()

    count = session.query(Media).count()
    is_last = (page*per_page >= count)

    album_list = session.query(Album).filter_by(parent_id=None).order_by(Album.id).all()[begin:end]

    links = {}
    if page != 1:
        links["previous"] = flask.url_for(self, page=page-1, per_page=per_page)
        links["first"] = flask.url_for(self, page=1, per_page=per_page)
    if not is_last:
        links["next"] = flask.url_for(self, page=page+1, per_page=per_page)
        links["last"] = flask.url_for(self, page=int(count/per_page), per_page=per_page)

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

    name = flask.request.form["name"]
    parent_id = flask.request.form.get("parent_id")
    if parent_id and session.query(Album).get(parent_id) is None:
        flask.abort(404)

    album = Album(name=name, parent_id=parent_id)
    session.add(album)
    session.commit()

    location = flask.url_for(
        "get_collection_item", table="album", id_=album.id)
    return json.dumps(album, cls=JSONEncoder), 201, { "Location": location }

@app.route("/api/collection/media", methods=["POST"])
def create_media():
    session = database.Session()

    if session.query(Album).get(flask.request.form["album_id"]) is None:
        flask.abort(404)

    arguments = {
        "title": flask.request.form["title"],
        "author": flask.request.form["author"],
        "album_id": flask.request.form["album_id"],
    }

    if "keywords" in flask.request.form:
        try:
            keywords = json.loads(flask.request.form["keywords"])
        except:
            flask.abort(400)
        else:
            arguments["keywords"] = keywords
    if "filename" in flask.request.form:
        arguments["filename"] = flask.request.form["filename"]

    media = Media(**arguments)
    session.add(media)
    session.commit()

    location = flask.url_for("get_collection_item", table="media", id_=media.id)
    return json.dumps(media, cls=JSONEncoder), 201, { "Location": location }

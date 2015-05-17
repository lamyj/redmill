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

import flask
import flask.json

from .. import database, models
from . import Base

import redmill

class Album(Base):

    def __init__(self):
        Base.__init__(self)

    def get(self, id_):
        if id_ is None:
            return self.get_roots()
        else:
            return self.get_album(id_)

    @Base.json_only
    @Base.authenticate()
    def post(self):
        session = database.Session()

        data = json.loads(flask.request.data)
        fields = ["name"]
        if any(field not in data for field in fields):
            flask.abort(400)

        parent_id = data.get("parent_id")
        if parent_id and session.query(models.Album).get(parent_id) is None:
            flask.abort(404)

        album = models.Album(name=data["name"], parent_id=parent_id)
        session.add(album)
        session.commit()

        location = flask.url_for(self.endpoint, id_=album.id)
        return flask.json.dumps(album), 201, { "Location": location }

    @Base.json_only
    @Base.authenticate()
    def put(self, id_):
        return self.update(id_)

    @Base.json_only
    @Base.authenticate()
    def patch(self, id_):
        return self.update(id_)

    @Base.json_only
    @Base.authenticate()
    def delete(self, id_):
        session = database.Session()
        value = session.query(models.Album).get(id_)
        if value is None:
            flask.abort(404)
        else:
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

    def get_roots(self):
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
        album_list = session.query(models.Album).filter_by(parent_id=None).order_by(models.Album.id).all()[begin:end]

        # Values in links are 1-based
        links = {}
        if page > 1:
            links["previous"] = flask.url_for(
                self.endpoint, page=(page+1)-1, per_page=per_page)
            links["first"] = flask.url_for(
                self.endpoint, page=1, per_page=per_page)
        if page < last_page:
            links["next"] = flask.url_for(
                self.endpoint, page=(page+1)+1, per_page=per_page)
            links["last"] = flask.url_for(
                self.endpoint, page=last_page+1, per_page=per_page)

        links = ", ".join(
            "<{}>; rel=\"{}\"".format(link, type_) for type_, link in links.items())

        if flask.request.headers.get("Accept") == "application/json":
            urls = [
                flask.url_for(self.endpoint, id_=album.id)
                for album in album_list
            ]
            return json.dumps(urls), 200 , {"Link": links, "Content-Type": "application/json"}
        else:
            albums = [
                (album.name, flask.url_for(self.endpoint, id_=album.id))
                for album in album_list
            ]
            return flask.render_template("main.html", albums=albums)

    def get_album(self, id_):
        session = database.Session()
        album = session.query(models.Album).get(id_)
        if album is None:
            flask.abort(404)
        else:
            if flask.request.headers.get("Accept") == "application/json":
                return flask.json.dumps(album)
            else:
                return flask.render_template("album.html", redmill=redmill, album=album)

    def update(self, id_):
        fields = ["name", "parent_id"]

        data = json.loads(flask.request.data)

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

        session.commit()

        return flask.json.dumps(item)

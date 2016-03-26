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

import io
import json
import os

import flask
import PIL.Image

from .. import database, magic, models, processor

from . import authenticate, get_item, jsonify, request_wants_json

def get_all(media_id):
    session = database.Session()

    # Make sure the request media exists.
    media = get_item(session, models.Media, media_id)

    derivatives = session.query(
        models.Derivative).filter_by(media_id=media_id).all()

    if request_wants_json():
        return jsonify([
            flask.url_for("derivative.get", media_id=media_id, id_=x.id)
            for x in derivatives])
    else:
        return as_html(TODO)

def get(media_id, id_):
    session = database.Session()

    derivative = session.query(models.Derivative).get((media_id, id_))
    if derivative is None:
        flask.abort(404)

    if request_wants_json():
        return jsonify(derivative)
    else:
        return as_html(derivative)

@authenticate()
def post(media_id):
    try:
        data = json.loads(flask.request.data.decode())
    except:
        flask.abort(400)

    fields = ["operations"]
    if any(field not in data for field in fields):
        flask.abort(400)

    session = database.Session()

    # Make sure the request media exists.
    media = get_item(session, models.Media, media_id)

    try:
        derivative = models.Derivative(media, data["operations"])
        session.add(derivative)
        session.commit()
    except Exception as e:
        session.rollback()
        flask.abort(500, e)

    view = __name__.split(".")[-1]
    endpoint = "{}.get".format(view)
    location = flask.url_for(endpoint, media_id=media.id, id_=derivative.id, _method="GET")
    return flask.json.dumps(derivative), 201, { "Location": location }

@authenticate()
def put(media_id, id_):
    return _update(media_id, id_)

@authenticate()
def patch(media_id, id_):
    return _update(media_id, id_)

@authenticate()
def delete(media_id, id_):
    session = database.Session()

    derivative = session.query(models.Derivative).get((media_id, id_))
    if derivative is None:
        flask.abort(404)
    else:
        try:
            session.delete(derivative)
        except Exception as e:
            session.rollback()
            flask.abort(500, e)
        session.commit()
        return "", 204 # No content

def as_html(derivative):
    parents = (
        [models.Album.get_toplevel()]+
        derivative.media.parents+[derivative.media])
    return flask.render_template(
        "derivative.html", derivative=derivative,
        operations=flask.json.dumps(derivative.operations), parents=parents)

@authenticate()
def create(media_id):
    session = database.Session()
    media = session.query(models.Media).get(media_id)
    if media is None:
        flask.abort(404)

def get_content(media_id, derivative_id):
    session = database.Session()

    derivative = session.query(models.Derivative).get((media_id, derivative_id))
    if derivative is None:
        flask.abort(404)

    # FIXME: this should be cached!
    filename = os.path.join(
        flask.current_app.config["media_directory"],
        "{}".format(derivative.media.id))
    image = PIL.Image.open(filename)

    thumbnail = processor.apply(derivative.operations, image)

    data = io.BytesIO()
    thumbnail.save(data, format="PNG")
    data = data.getvalue()

    headers = {
        "Content-Type": magic.buffer(data),
    }

    return data, 200, headers

def _update(media_id, id_):
    try:
        data = json.loads(flask.request.data)
    except Exception as e:
        flask.abort(400)

    session = database.Session()

    derivative = session.query(models.Derivative).get((media_id, id_))
    if derivative is None:
        flask.abort(404)

    fields = ["operations"]
    for field in data:
        if field not in fields:
            flask.abort(400)

    if flask.request.method == "PUT":
        if set(data.keys()) != set(fields):
            flask.abort(400)

    for field, value in data.items():
        setattr(derivative, field, value)

    session.commit()

    return flask.json.dumps(derivative)

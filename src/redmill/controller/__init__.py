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

import flask
import itsdangerous

import redmill

from json_encoder import JSONEncoder
from .. import views

def register_collection(app, cls, endpoint):
    cls.endpoint = endpoint
    view_function = cls.as_view(cls.endpoint)

    app.add_url_rule(
        "/{}/".format(endpoint), defaults={"id_": None},
        view_func=view_function, methods=["GET"])

    app.add_url_rule(
        "/{}/".format(endpoint), view_func=view_function, methods=["POST"])

    app.add_url_rule(
        "/{}/<int:id_>".format(endpoint), view_func=view_function,
        methods=["GET", "PUT", "PATCH", "DELETE"])

def register_item(app, cls, endpoint, template):
    cls.endpoint = endpoint
    view_function = cls.as_view(cls.endpoint)

    app.add_url_rule(
        template, view_func=view_function,
        methods=["GET", "POST", "PUT", "PATCH", "DELETE"])

app = flask.Flask("redmill")
app.config["authenticator"] = None
app.config["max_token_age"] = 3600
app.config["media_directory"] = None
app.config["serializer"] = lambda: itsdangerous.URLSafeTimedSerializer(
    app.config["SECRET_KEY"], "token")
app.json_encoder = JSONEncoder

register_collection(app, views.Album, "albums")
register_collection(app, views.Media, "media")
register_item(app, views.MediaContent, "media_content", "/media/<int:id_>/content")
register_item(app, views.CreateAlbum, "create_album", "/albums/<int:id_>/create")
app.add_url_rule("/albums/create", "create_root_album", lambda: views.CreateAlbum().get())
register_item(app, views.Token, "token", "/token")

@app.context_processor
def inject_user():
    return dict(redmill=redmill)

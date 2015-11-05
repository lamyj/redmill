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
import register
from .. import views

app = flask.Flask("redmill")
app.config["authenticator"] = None
app.config["max_token_age"] = 3600
app.config["media_directory"] = None
app.config["serializer"] = lambda: itsdangerous.URLSafeTimedSerializer(
    app.config["SECRET_KEY"], "token")
app.json_encoder = JSONEncoder
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

register.register_collection(app, views.album, "/albums")
app.add_url_rule(
    "/", "root", views.album.get_roots, methods=["GET"])
app.add_url_rule(
    "/albums/", "album.get_roots", views.album.get_roots, methods=["GET"])
app.add_url_rule(
    "/albums/<int:parent_id>/create", "album.create", views.album.create,
    methods=["GET"])
app.add_url_rule(
    "/albums/create", "album.create_root", views.album.create,
    methods=["GET"])
app.add_url_rule(
    "/albums/<int:id_>/order_children", "album.order_children",
    views.album.order_children, methods=["POST"])
app.add_url_rule(
    "/albums/order_children", "album.order_children_root",
    lambda: views.album.order_children(None), methods=["POST"])


register.register_collection(app, views.media, "/media")
app.add_url_rule(
    "/albums/<int:parent_id>/create_media", "media.create", views.media.create,
    methods=["GET"])

register.register_item(app, views.media_content, "/media/<int:id_>/content")
register.register_item(app, views.token, "/token")

@app.context_processor
def inject_user():
    return dict(redmill=redmill, isinstance=isinstance)

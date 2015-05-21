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

import functools

import flask
import flask.views
import itsdangerous

def token_authenticator(request):
    if request.authorization is None:
        return False
    username = request.authorization.get("username")
    try:
        flask.current_app.config["serializer"]().make_signer().unsign(
            username, max_age=flask.current_app.config["max_token_age"])
    except itsdangerous.BadSignature:
        return False
    else:
        return True

class Base(flask.views.MethodView):

    def __init__(self):
        flask.views.MethodView.__init__(self)

    @staticmethod
    def authenticate(login_only=False):
        def decorator(function):
            @functools.wraps(function)
            def wrapper(*args, **kwargs):
                authenticators = [flask.current_app.config["authenticator"]]
                if not login_only:
                    authenticators.insert(0, token_authenticator)

                authenticated = False
                for authenticator in authenticators:
                    authenticated = authenticator(flask.request)
                    if authenticated:
                        break

                if not authenticated:
                    if flask.request.headers.get("Accept") == "application/json":
                        flask.abort(401)
                    else:
                        # go to login
                        flask.abort(401)
                else:
                    return function(*args, **kwargs)

            return wrapper
        return decorator

    def request_wants_json(self):
        accept_mimetypes = flask.request.accept_mimetypes
        best = accept_mimetypes.best_match(["application/json", "text/html"])
        return (
            best == "application/json" and
            accept_mimetypes[best] > accept_mimetypes["text/html"])

    def jsonify(self, data, *args, **kwargs):
        json_data = flask.json.dumps(data)
        return flask.Response(
            json_data, *args, mimetype="application/json", **kwargs)

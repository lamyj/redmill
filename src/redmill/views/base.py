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

class Base(flask.views.MethodView):

    endpoint = None

    def __init__(self):
        flask.views.MethodView.__init__(self)

    @staticmethod
    def json_only(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            if flask.request.headers.get("Accept") != "application/json":
                flask.abort(406, "JSON-only method")
            else:
                return function(*args, **kwargs)
        return wrapper

    @staticmethod
    def authenticate(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            authenticators = [flask.current_app.config["authenticator"]]
            #if not login_only:
            #    authenticators.insert(0, token_authenticator)

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

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
import itsdangerous

app = flask.Flask(__name__)
app.config["authenticator"] = None
app.config["max_token_age"] = 3600
app.config["media_directory"] = None
app.config["serializer"] = lambda: itsdangerous.URLSafeTimedSerializer(
    app.config["SECRET_KEY"], "token")

def token_authenticator(request):
    if request.authorization is None:
        return
    username = request.authorization.get("username")
    try:
        app.config["serializer"]().make_signer().unsign(
            username, max_age=app.config["max_token_age"])
    except itsdangerous.BadSignature:
        return False
    else:
        return True

def authenticate(login_only=False):
    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            authenticators = [app.config["authenticator"]]
            if not login_only:
                authenticators.insert(0, token_authenticator)

            authenticated = False
            for authenticator in authenticators:
                authenticated = authenticator(flask.request)
                if authenticated:
                    break

            if not authenticated:
                flask.abort(401)
            else:
                return function(*args, **kwargs)
        return wrapper
    return decorator

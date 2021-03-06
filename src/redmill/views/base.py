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

import redmill.models

def get_item(session, model, id_):
    item = session.query(model).get(id_)

    if item is None:
        flask.abort(404)
    elif not all([x.status == "published" for x in item.parents+[item]]) and not is_authenticated():
        flask.abort(404)

    return item

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

def is_authenticated(login_only=False):
    authenticators = [flask.current_app.config["authenticator"]]
    if not login_only:
        authenticators.insert(0, token_authenticator)

    authenticated = False
    for authenticator in authenticators:
        authenticated = authenticator(flask.request)
        if authenticated:
            break

    return authenticated

def authenticate(login_only=False):
    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            authenticated = is_authenticated(login_only)

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

def request_wants_json():
    accept_mimetypes = flask.request.accept_mimetypes
    best = accept_mimetypes.best_match(["application/json", "text/html"])
    return (
        best == "application/json" and
        accept_mimetypes[best] > accept_mimetypes["text/html"])

def jsonify(data, *args, **kwargs):
    json_data = flask.json.dumps(data)
    return flask.Response(
        json_data, *args, mimetype="application/json", **kwargs)

def get_children_filter():
    children_filter = flask.request.args.get("children")
    if not children_filter:
        children_filter = ["published"]
    else:
        children_filter = children_filter.split("|")

    return children_filter

def get_tree(limit):

    def get_children_list(album, mode, top_level=True, disabled=False):
        if mode=="album" or album.id:
            onclick = "onclick=\"alert('{}');\"".format(album.id)
            class_ = "enabled"
        else:
            onclick = ""
            class_ = "disabled"

        if album.id == limit:
            disabled = True
        result = u"<span class=\"{}\" data-rm-id=\"{}\" {}>{}</span>".format(
            class_, album.id or "", "disabled=\"disabled\"" if disabled else "",
            album.name)

        children = [
            u"<li>{}</li>".format(get_children_list(x, mode, False, disabled))
            for x in album.children if x.type == "album"]
        if children:
            result += u"<ul>{}</ul>".format("".join(children))

        return (u"<ul class=\"tree\"><li>{}</li></ul>" if top_level else u"{}").format(result)

    # Display it somehow on the left to make a move widget
    # Same code for media and album

    return get_children_list(redmill.models.Album.get_toplevel(), "album")

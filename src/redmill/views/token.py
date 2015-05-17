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
import flask.json

from . import Base

class Token(Base):

    def __init__(self):
        Base.__init__(self)

    @Base.json_only
    @Base.authenticate(True)
    def get(self):
        token = flask.current_app.config["serializer"]().dumps(
            {"user": flask.request.authorization["username"]})
        return flask.json.dumps({"token": token})
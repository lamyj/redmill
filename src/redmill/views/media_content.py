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

import base64
import os

import flask

from .. import app, database, magic, models
from . import Base

class MediaContent(Base):

    def __init__(self):
        Base.__init__(self)

    def get(self, id_):
        session = database.Session()
        media = session.query(models.Media).get(id_)
        if media is None:
            flask.abort(404)

        filename = os.path.join(app.config["media_directory"], "{}".format(media.id))
        with open(filename, "rb") as fd:
            data = fd.read()

        headers = {
            "Content-Type": magic.buffer(data),
            "Content-Disposition": "inline; filename=\"{}\"".format(media.filename)
        }

        return data, 200, headers

    @Base.json_only
    @Base.authenticate
    def patch(self, id_):
        return self.update(id_)

    @Base.json_only
    @Base.authenticate
    def put(self, id_):
        return self.update(id_)

    def update(self, id_):
        session = database.Session()
        media = session.query(models.Media).get(id_)
        if media is None:
            flask.abort(404)

        content = base64.b64decode(flask.request.data)

        filename = os.path.join(app.config["media_directory"], "{}".format(media.id))
        with open(filename, "wb") as fd:
            fd.write(content)

        return "", 200

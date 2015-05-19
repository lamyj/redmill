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

class CreateAlbum(Base):

    def __init__(self):
        Base.__init__(self)

    def get(self, id_=None):
        session = database.Session()
        if id_ is not None:
            album = session.query(models.Album).get(id_)
            if album is None:
                flask.abort(404)
        else:
            album = None

        return flask.render_template("create_album.html", album=album)

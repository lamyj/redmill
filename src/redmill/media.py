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

import os

import sqlalchemy
import sqlalchemy.orm

import redmill.database

class Media(redmill.database.Base):
    __tablename__ = "media"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    title = sqlalchemy.Column(sqlalchemy.Unicode, nullable=False)
    author = sqlalchemy.Column(sqlalchemy.Unicode, nullable=False)
    keywords = sqlalchemy.Column(redmill.database.JSON)
    filename = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    album_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('album.id'))

    album = sqlalchemy.orm.relationship(
        "Album", backref=sqlalchemy.orm.backref("media"))

    def __init__(self, *args, **kwargs):
        if "content" in kwargs:
            content = kwargs["content"]
            del kwargs["content"]
        else:
            content = None
        redmill.database.Base.__init__(self, *args, **kwargs)
        if not self.filename:
            self.filename = redmill.database.get_filesystem_path(self.title, content)

    def __eq__(self, other):
        return isinstance(other, type(self)) and other.id == self.id

    def _get_location(self):
        return os.path.join(self.album.path, self.filename)

    location = property(_get_location)

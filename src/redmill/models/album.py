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

import redmill.database

from . import Base

class Album(Base):
    __tablename__ = "album"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.Unicode, nullable=False)
    parent_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("album.id"))

    children = sqlalchemy.orm.relationship("Album")

    def __eq__(self, other):
        return isinstance(other, type(self)) and other.id == self.id

    def _get_parent(self):
        if self.parent_id is None:
            parent = None
        else:
            session = redmill.database.Session()
            parent = session.query(Album).filter_by(id=self.parent_id).one()
        return parent

    def _get_parents(self):
        album = self
        parents = []
        while album.parent is not None:
            parents.insert(0, album.parent)
            album = album.parent
        return parents

    def _get_path(self):
        album = self
        path = []
        while album is not None:
            path.insert(0, redmill.database.get_filesystem_path(album.name))
            album = album.parent
        return os.path.join(*path)

    parent = property(_get_parent)
    parents = property(_get_parents)
    path = property(_get_path)

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

from . import Item

class Album(Item):
    __tablename__ = "album"

    id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("item.id"), primary_key=True)

    __mapper_args__ = { "polymorphic_identity": "album" }

    @staticmethod
    def get_toplevel():
        session = redmill.database.Session()
        album = Album(
            id=None, name="Gallery root", parent_id=None,
            children=session.query(Album)\
                .filter_by(parent_id=None)\
                .order_by(Album.rank)\
                .all())
        return album

Item.sub_types.append(Album)

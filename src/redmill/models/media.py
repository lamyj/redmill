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

class Media(Item):
    __tablename__ = "media"

    id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("item.id"), primary_key=True)
    author = sqlalchemy.Column(sqlalchemy.Unicode, nullable=False)
    keywords = sqlalchemy.Column(redmill.database.JSON)
    filename = sqlalchemy.Column(sqlalchemy.String)

    __mapper_args__ = { "polymorphic_identity": "media" }

    def __init__(self, *args, **kwargs):
        content = kwargs.pop("content", None)
        Item.__init__(self, *args, **kwargs)
        if not self.filename and content:
            self.filename = redmill.database.get_filesystem_path(self.name, content)

Item.sub_types.append(Media)

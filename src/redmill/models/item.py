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

import datetime

import sqlalchemy
import sqlalchemy.orm

from . import Base

class Item(Base):
    sub_types = []

    __tablename__ = "item"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.Unicode, nullable=False)
    type = sqlalchemy.Column(sqlalchemy.String)
    rank = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    parent_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("item.id"))

    Status = ("published", "archived")
    status = sqlalchemy.Column(sqlalchemy.Enum(*Status), default="published")

    created_at = sqlalchemy.Column(
        sqlalchemy.DateTime, default=lambda: datetime.datetime.now())
    modified_at = sqlalchemy.Column(
        sqlalchemy.DateTime, nullable=True)

    children = sqlalchemy.orm.relationship(
        "Item", lazy="immediate", order_by="asc(Item.rank)")

    __mapper_args__ = { "polymorphic_identity": "item", "polymorphic_on": type }

    def __hash__(self):
        return hash(str(self.id)+self.type)
    
    def __eq__(self, other):
        return self.id == other.id

    def _get_parent(self):
        if self.parent_id is None:
            parent = None
        else:
            parent = sqlalchemy.orm.object_session(self).query(
                sqlalchemy.orm.with_polymorphic(Item, Item.sub_types))\
                .filter_by(id=self.parent_id).one()

        return parent

    def _get_parents(self):
        current = self
        parents = []
        while current.parent_id is not None:
            parents.insert(0, current.parent)
            current = current.parent
        return parents

    parent = property(_get_parent)
    parents = property(_get_parents)

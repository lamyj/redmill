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

import sqlalchemy
import sqlalchemy.orm

import redmill.database

from . import Base, Media

class Derivative(Base):
    """ Derivative of an image (e.g. thumbnail or resized version).
    """

    __tablename__ = "derivative"

    media_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("media.id"), primary_key=True)
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    operations = sqlalchemy.Column(redmill.database.JSON)

    media = sqlalchemy.orm.relationship(
        "Media", backref=sqlalchemy.orm.backref("derivatives"))

    def __init__(self, media, operations, id_=None):
        """ Operations must be a list of (operation_type, parameters). Media
            can be media or its id.
        """

        if isinstance(media, Media):
            media_id = media.id
        else:
            media_id = media
            session = redmill.database.Session()
            media = session.query(Media).filter_by(id=media_id)

        if id_ is None:
            session = redmill.database.Session()
            id_ = media.next_derivative
            media.next_derivative += 1
            session.commit()

        for type_, parameters in operations:
            if type_ not in dir(redmill.processor):
                raise NotImplementedError("Unknown operation: {}".format(type_))

        Base.__init__(self, media_id=media_id, id=id_, operations=operations)

    def __eq__(self, other):
        return (
            isinstance(other, type(self)) and
            other.media_id == self.media_id and other.id == self.id)

    def process(self, image):
        """ Apply the operations to given PIL.Image.
        """

        return redmill.processor.apply(self.operations, image)

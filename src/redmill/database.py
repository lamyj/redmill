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

import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm

import unidecode

Base = sqlalchemy.ext.declarative.declarative_base()
Session = sqlalchemy.orm.sessionmaker()

def get_filesystem_path(name):
    return unidecode.unidecode(name.replace(" ", "_"))

class JSON(sqlalchemy.types.TypeDecorator):

    impl = sqlalchemy.types.String

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        return json.loads(value)
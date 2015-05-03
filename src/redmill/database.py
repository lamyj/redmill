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
import mimetypes
import os

import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm

import unidecode

from . import magic

Base = sqlalchemy.ext.declarative.declarative_base()
Session = sqlalchemy.orm.sessionmaker()

def get_filesystem_path(name, data=None):
    if data:
        mime_type = magic.buffer(data)

        blacklist = [".jpe", ".jpeg"]
        suffix_map = {
            type_: suffix
            for suffix, type_ in mimetypes.types_map.items()
            if suffix not in blacklist
        }
        extension = suffix_map[mime_type]
    else:
        extension = ""

    return "{}{}".format(unidecode.unidecode(name.replace(" ", "_")), extension)

class JSON(sqlalchemy.types.TypeDecorator):

    impl = sqlalchemy.types.String

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        return json.loads(value)

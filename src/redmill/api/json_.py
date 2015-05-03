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

import flask
import flask.json
from .. import Album, Media

class JSONEncoder(flask.json.JSONEncoder):
    """ Encode database objects to JSON.
    """

    def default(self, obj):
        if isinstance(obj, (Album, Media)):
            fields = {
                Album: ["id", "name", "parent_id"],
                Media: [
                    "id", "title", "author", "keywords", "filename", "album_id",
                    "location"
                ]
            }

            type_ = type(obj)
            value = { field: getattr(obj, field) for field in fields[type_] }
            value["type"] = type_.__name__

            if isinstance(obj, Album):
                children = [("album", x.id) for x in obj.children]
                children += [("media", x.id) for x in obj.media]

                value["children"] = [
                    flask.url_for("get_collection_item", table=table, id_=id_)
                    for table, id_ in children]
        else:
            value = obj
        return value

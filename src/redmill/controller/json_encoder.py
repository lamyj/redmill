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
import flask
import flask.json
from .. import models, views

class JSONEncoder(flask.json.JSONEncoder):
    """ Encode database objects to JSON.
    """

    def default(self, obj):
        if isinstance(obj, (models.Album, models.Media)):
            fields = {
                "common": [
                    "id", "name", "parent_id", "status", "created_at",
                    "modified_at"],
                models.Album: [],
                models.Media: ["author", "keywords", "filename"]
            }

            type_ = type(obj)
            value = {
                field: getattr(obj, field)
                for field in fields["common"]+fields[type_] }
            value["type"] = type_.__name__

            if isinstance(obj, models.Album):
                children = [(x.type, x.id) for x in obj.children]

                value["children"] = [
                    flask.url_for("{}.get".format(collection), id_=id_)
                    for collection, id_ in children]
        elif isinstance(obj, models.Derivative):
            fields = ["media_id", "id", "operations"]
            value = { field: getattr(obj, field) for field in fields }
        elif isinstance(obj, datetime.datetime):
            value = obj.isoformat()
        else:
            value = flask.json.JSONEncoder.default(self, obj)
        return value

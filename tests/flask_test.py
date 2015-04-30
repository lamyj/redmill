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
import redmill
import database_test

class FlaskTest(database_test.DatabaseTest):
    def setUp(self):
        database_test.DatabaseTest.setUp(self)
        self.app = redmill.app.test_client()

    def _get_response(self, method, url, *args, **kwargs):
        response = getattr(self.app, method)(url, *args, **kwargs)

        if response.status_code/100 not in [4,5]:
            if response.data:
                data = json.loads(response.data)
            else:
                data = None
        else:
            data = response.data

        return response.status_code, response.headers, data

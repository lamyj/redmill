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

import unittest
import sqlalchemy
import redmill.database

class DatabaseTest(unittest.TestCase):

    def setUp(self):
        self.engine = sqlalchemy.create_engine("sqlite:///:memory:")
        redmill.database.Base.metadata.create_all(self.engine)

        redmill.database.Session.configure(bind=self.engine)
        self.session = redmill.database.Session()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

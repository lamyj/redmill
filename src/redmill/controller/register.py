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

def register(app, module, urls):
    for method, url in urls.items():
        function = getattr(module, method.lower(), None)
        if function is not None:
            endpoint = "{}.{}".format(
                module.__name__.split(".")[-1],
                function.__name__)
            app.add_url_rule(
                url, endpoint, function, methods=[method])


def register_collection(app, module, mount_point):
    urls = {
        method: os.path.join(mount_point, "<int:id_>")
        for method in ["GET", "PUT", "PATCH", "DELETE"]
    }
    urls["POST"] = os.path.join(mount_point, "")

    register(app, module, urls)

def register_item(app, module, mount_point):
    urls = {
        method: mount_point
        for method in ["GET", "POST", "PUT", "PATCH", "DELETE"]
    }

    register(app, module, urls)

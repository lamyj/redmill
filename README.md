# redmill

[![Build Status](https://travis-ci.org/lamyj/redmill.svg?branch=master)](https://travis-ci.org/lamyj/redmill)

Redmill is a web-based picture manager geared toward web sites that regularly
publish images. With both a web-based interface and a REST API, users can easily
set keywords and create derivatives (e.g. thumbnails or crops) and embed them
in the web sites.

## Installation

Make sure you have all the dependencies:

* [SQLAlchemy](http://www.sqlalchemy.org/) (1.0.2)
* [Flask](http://flask.pocoo.org/) (>= 0.10.1)
* [itsdangerous](https://pythonhosted.org/itsdangerous/) (>= 0.24)
* [Unidecode](https://pypi.python.org/pypi/Unidecode) (>= 0.4.17)

To run the unit tests, you will also need [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/).

Get the [latest release](https://github.com/lamyj/redmill/releases) or the
[bleeding edge revision](https://github.com/lamyj/redmill).

Configure the application, e.g.

```python
redmill.controller.app.config["media_directory"] = "/some/where"
redmill.controller.app.config["SECRET_KEY"] = "deadbeef"
redmill.controller.app.config["authenticator"] = lambda x: True
```

[Deploy it](http://flask.pocoo.org/docs/0.10/deploying/) your favorite way!

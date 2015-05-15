import sqlalchemy.ext.declarative

Base = sqlalchemy.ext.declarative.declarative_base()

from album import Album
from media import Media

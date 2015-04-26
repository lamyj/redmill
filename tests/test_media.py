# encoding: utf-8

import unittest

import sqlalchemy
import sqlalchemy.orm

import redmill.database

class TestMedia(unittest.TestCase):

    def setUp(self):
        self.engine = sqlalchemy.create_engine("sqlite:///:memory:", echo=False)
        redmill.database.Base.metadata.create_all(self.engine)

        redmill.database.Session = sqlalchemy.orm.sessionmaker(bind=self.engine)
        redmill.database.session = redmill.database.Session()

        self.album = redmill.Album(name=u"Röôt album")
        redmill.database.session.add(self.album)
        redmill.database.session.commit()

    def tearDown(self):
        pass

    def test_constructor(self):
        media = redmill.Media(
            title=u"Mÿ îmage", author=u"John Doe",
            keywords=["foo", "bar"], album_id=self.album.id)

        self.assertEqual(media.filename, "My_image")

        redmill.database.session.add(media)
        redmill.database.session.commit()

        self.assertEqual(media.album, self.album)
        self.assertEqual(len(media.album.media), 1)
        self.assertEqual(media.album.media[0], media)

        media_collection = [x for x in redmill.database.session.query(redmill.Media)]
        self.assertEqual(len(media_collection), 1)
        self.assertEqual(media_collection[0].title, u"Mÿ îmage")
        self.assertEqual(media_collection[0].author, "John Doe")
        self.assertEqual(media_collection[0].keywords, ["foo", "bar"])

        self.assertEqual(media_collection[0].location, "Root_album/My_image")

if __name__ == '__main__':
    unittest.main()

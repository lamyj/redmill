# encoding: utf-8

import unittest
import redmill.database
import database_test

class TestMedia(database_test.DatabaseTest):

    def setUp(self):
        database_test.DatabaseTest.setUp(self)

        self.album = redmill.Album(name=u"Röôt album")
        self.session.add(self.album)
        self.session.commit()

    def test_constructor(self):
        media = redmill.Media(
            title=u"Mÿ îmage", author=u"John Doe",
            keywords=["foo", "bar"], album_id=self.album.id)

        self.assertEqual(media.filename, "My_image")

        self.session.add(media)
        self.session.commit()

        self.assertEqual(media.album, self.album)
        self.assertEqual(len(media.album.media), 1)
        self.assertEqual(media.album.media[0], media)

        media_collection = [x for x in self.session.query(redmill.Media)]
        self.assertEqual(len(media_collection), 1)
        self.assertEqual(media_collection[0].title, u"Mÿ îmage")
        self.assertEqual(media_collection[0].author, "John Doe")
        self.assertEqual(media_collection[0].keywords, ["foo", "bar"])

        self.assertEqual(media_collection[0].location, "Root_album/My_image")

if __name__ == "__main__":
    unittest.main()

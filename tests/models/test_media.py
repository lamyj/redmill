# encoding: utf-8

import os
import sys
import unittest

import redmill.database
import redmill.models

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database_test import DatabaseTest

class TestMedia(DatabaseTest):

    def setUp(self):
        DatabaseTest.setUp(self)

        self.album = redmill.models.Album(name=u"Röôt album")
        self.session.add(self.album)
        self.session.commit()

    def test_constructor(self):
        media = redmill.models.Media(
            title=u"Mÿ îmage", author=u"John Doe", keywords=["foo", "bar"],
            filename="My_image.jpg", album_id=self.album.id)

        self.session.add(media)
        self.session.commit()

        self.assertEqual(media.album, self.album)
        self.assertEqual(len(media.album.media), 1)
        self.assertEqual(media.album.media[0], media)

        media_collection = [x for x in self.session.query(redmill.models.Media)]
        self.assertEqual(len(media_collection), 1)
        self.assertEqual(media_collection[0].title, u"Mÿ îmage")
        self.assertEqual(media_collection[0].author, "John Doe")
        self.assertEqual(media_collection[0].keywords, ["foo", "bar"])
        self.assertEqual(media_collection[0].filename, "My_image.jpg")

        self.assertEqual(media_collection[0].location, "Root_album/My_image.jpg")

    def test_constructor_without_filename(self):
        # From https://www.flickr.com/photos/britishlibrary/11005918694/
        filename = os.path.join(os.path.dirname(__file__), "..", "image.jpg")
        content = open(filename, "rb").read()
        media = redmill.models.Media(
            title=u"Mÿ îmage", author=u"John Doe", keywords=["foo", "bar"],
            album_id=self.album.id, content=content)

        self.session.add(media)
        self.session.commit()

        self.assertEqual(media.album, self.album)
        self.assertEqual(len(media.album.media), 1)
        self.assertEqual(media.album.media[0], media)

        media_collection = [x for x in self.session.query(redmill.models.Media)]
        self.assertEqual(len(media_collection), 1)
        self.assertEqual(media_collection[0].title, u"Mÿ îmage")
        self.assertEqual(media_collection[0].author, "John Doe")
        self.assertEqual(media_collection[0].keywords, ["foo", "bar"])
        self.assertEqual(media_collection[0].filename, "My_image.jpg")

        self.assertEqual(media_collection[0].location, "Root_album/My_image.jpg")

if __name__ == "__main__":
    unittest.main()

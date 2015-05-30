# encoding: utf-8

import os
import unittest
import sys

import redmill.database
import redmill.models

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database_test import DatabaseTest

class TestAlbum(DatabaseTest):

    def test_constructor(self):
        foo = redmill.models.Album(name=u"foo")
        self.session.add(foo)

        albums = [x for x in self.session.query(redmill.models.Album)]

        self.assertEqual(len(albums), 1)
        self.assertEqual(albums[0].name, "foo")
        self.assertEqual(albums[0].parent_id, None)
        self.assertEqual(len(albums[0].children), 0)

if __name__ == "__main__":
    unittest.main()

# encoding: utf-8

import os
import sys
import unittest

import redmill.models

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database_test import DatabaseTest

class TestDerivative(DatabaseTest):

    def setUp(self):
        DatabaseTest.setUp(self)

        self.album = redmill.models.Album(name=u"Röôt album")
        self.session.add(self.album)
        self.session.commit()

        self.media = redmill.models.Media(
            name=u"Mÿ îmage", author=u"John Doe",
            keywords=["foo", "bar"], parent_id=self.album.id)
        self.session.add(self.media)
        self.session.commit()

    def tearDown(self):
        pass

    def test_constructor(self):
        derivative = redmill.models.Derivative(
            [
                ("rotate", (1.234,)),
                ("resize", (40, "20%",))
            ],
            self.media)
        self.session.add(derivative)
        self.session.commit()

        derivatives = self.session.query(redmill.models.Derivative).all()
        self.assertEqual(len(derivatives), 1)

        self.assertEqual(derivatives[0].media_id, self.media.id)

        self.assertEqual(len(derivatives[0].operations), 2)
        self.assertEqual(derivatives[0].operations[0], ["rotate", [1.234,]])
        self.assertEqual(derivatives[0].operations[1], ["resize", [40, "20%"]])

        self.assertEqual(derivatives[0].media, self.media)

if __name__ == '__main__':
    unittest.main()

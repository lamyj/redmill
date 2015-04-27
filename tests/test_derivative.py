# encoding: utf-8

import unittest
import redmill.database
import database_test

class TestDerivative(database_test.DatabaseTest):

    def setUp(self):
        database_test.DatabaseTest.setUp(self)

        self.album = redmill.Album(name=u"Röôt album")
        self.session.add(self.album)
        self.session.commit()

        self.media = redmill.Media(
            title=u"Mÿ îmage", author=u"John Doe",
            keywords=["foo", "bar"], album_id=self.album.id)
        self.session.add(self.media)
        self.session.commit()

    def tearDown(self):
        pass

    def test_constructor(self):
        derivative = redmill.Derivative(
            [
                ("rotate", (1.234,)),
                ("resize", (40, "20%",))
            ],
            self.media)
        self.session.add(derivative)
        self.session.commit()

        derivatives = self.session.query(redmill.Derivative).all()
        self.assertEqual(len(derivatives), 1)

        self.assertEqual(derivatives[0].media_id, self.media.id)

        self.assertEqual(len(derivatives[0].operations), 2)
        self.assertEqual(derivatives[0].operations[0], ["rotate", [1.234,]])
        self.assertEqual(derivatives[0].operations[1], ["resize", [40, "20%"]])

        self.assertEqual(derivatives[0].media, self.media)

if __name__ == '__main__':
    unittest.main()

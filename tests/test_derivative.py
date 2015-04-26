# encoding: utf-8

import unittest

import sqlalchemy
import sqlalchemy.orm

import redmill.database

class TestDerivative(unittest.TestCase):

    def setUp(self):
        self.engine = sqlalchemy.create_engine("sqlite:///:memory:", echo=False)
        redmill.database.Base.metadata.create_all(self.engine)

        redmill.database.Session = sqlalchemy.orm.sessionmaker(bind=self.engine)
        redmill.database.session = redmill.database.Session()

        self.album = redmill.Album(name=u"Röôt album")
        redmill.database.session.add(self.album)
        redmill.database.session.commit()

        self.media = redmill.Media(
            title=u"Mÿ îmage", author=u"John Doe",
            keywords=["foo", "bar"], album_id=self.album.id)
        redmill.database.session.add(self.media)
        redmill.database.session.commit()

    def tearDown(self):
        pass

    def test_constructor(self):
        derivative = redmill.Derivative(
            [
                ("rotate", (1.234,)),
                ("resize", (40, "20%",))
            ],
            self.media)
        redmill.database.session.add(derivative)
        redmill.database.session.commit()

        derivatives = redmill.database.session.query(redmill.Derivative).all()
        self.assertEqual(len(derivatives), 1)

        self.assertEqual(derivatives[0].media_id, self.media.id)

        self.assertEqual(len(derivatives[0].operations), 2)
        self.assertEqual(derivatives[0].operations[0], ["rotate", [1.234,]])
        self.assertEqual(derivatives[0].operations[1], ["resize", [40, "20%"]])

        self.assertEqual(derivatives[0].media, self.media)

if __name__ == '__main__':
    unittest.main()

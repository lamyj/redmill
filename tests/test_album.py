# encoding: utf-8

import unittest

import sqlalchemy
import sqlalchemy.orm

import redmill.database

class TestAlbum(unittest.TestCase):

    def setUp(self):
        self.engine = sqlalchemy.create_engine("sqlite:///:memory:", echo=False)
        redmill.database.Base.metadata.create_all(self.engine)

        redmill.database.Session = sqlalchemy.orm.sessionmaker(bind=self.engine)
        redmill.database.session = redmill.database.Session()

    def tearDown(self):
        pass

    def test_constructor(self):
        foo = redmill.Album(name=u"foo")
        redmill.database.session.add(foo)

        albums = [x for x in redmill.database.session.query(redmill.Album)]

        self.assertEqual(len(albums), 1)
        self.assertEqual(albums[0].name, "foo")
        self.assertEqual(albums[0].parent_id, None)
        self.assertEqual(len(albums[0].children), 0)

    def test_child(self):
        foo = redmill.Album(name=u"foo")
        redmill.database.session.add(foo)
        redmill.database.session.commit()

        bar = redmill.Album(name=u"bar", parent_id=foo.id)
        redmill.database.session.add(bar)
        redmill.database.session.commit()

        self.assertEqual(bar.parent_id, foo.id)

        self.assertEqual(len(foo.children), 1)
        self.assertEqual(foo.children[0], bar)

    def test_parent(self):
        foo = redmill.Album(name=u"foo")
        redmill.database.session.add(foo)
        redmill.database.session.commit()

        bar = redmill.Album(name=u"bar", parent_id=foo.id)
        redmill.database.session.add(bar)
        redmill.database.session.commit()

        self.assertEqual(foo.parent, None)
        self.assertEqual(bar.parent, foo)

    def test_path(self):
        foo = redmill.Album(name=u"föo")
        redmill.database.session.add(foo)
        redmill.database.session.commit()

        bar = redmill.Album(name=u"bâr", parent_id=foo.id)
        redmill.database.session.add(bar)
        redmill.database.session.commit()

        self.assertEqual(foo.path, "foo")
        self.assertEqual(bar.path, "foo/bar")

if __name__ == '__main__':
    unittest.main()

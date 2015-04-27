# encoding: utf-8

import unittest
import redmill.database
import database_test

class TestAlbum(database_test.DatabaseTest):

    def test_constructor(self):
        foo = redmill.Album(name=u"foo")
        self.session.add(foo)

        albums = [x for x in self.session.query(redmill.Album)]

        self.assertEqual(len(albums), 1)
        self.assertEqual(albums[0].name, "foo")
        self.assertEqual(albums[0].parent_id, None)
        self.assertEqual(len(albums[0].children), 0)

    def test_child(self):
        foo = redmill.Album(name=u"foo")
        self.session.add(foo)
        self.session.commit()

        bar = redmill.Album(name=u"bar", parent_id=foo.id)
        self.session.add(bar)
        self.session.commit()

        self.assertEqual(bar.parent_id, foo.id)

        self.assertEqual(len(foo.children), 1)
        self.assertEqual(foo.children[0], bar)

    def test_parent(self):
        foo = redmill.Album(name=u"foo")
        self.session.add(foo)
        self.session.commit()

        bar = redmill.Album(name=u"bar", parent_id=foo.id)
        self.session.add(bar)
        self.session.commit()

        self.assertEqual(foo.parent, None)
        self.assertEqual(bar.parent, foo)

    def test_path(self):
        foo = redmill.Album(name=u"föo")
        self.session.add(foo)
        self.session.commit()

        bar = redmill.Album(name=u"bâr", parent_id=foo.id)
        self.session.add(bar)
        self.session.commit()

        self.assertEqual(foo.path, "foo")
        self.assertEqual(bar.path, "foo/bar")

if __name__ == "__main__":
    unittest.main()

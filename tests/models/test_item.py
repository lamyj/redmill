import datetime
import os
import unittest
import sys

import redmill.database
import redmill.models

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database_test import DatabaseTest

class TestItem(DatabaseTest):

    def test_constructor(self):
        foo = redmill.models.Item(name=u"foo")
        self.session.add(foo)

        items = [x for x in self.session.query(redmill.models.Item)]

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0], foo)
        self.assertEqual(items[0].name, "foo")
        self.assertEqual(items[0].parent_id, None)
        self.assertEqual(items[0].children, [])
        self.assertTrue(items[0].created_at <= datetime.datetime.now())
        self.assertTrue(items[0].modified_at is None)

    def test_children(self):
        foo = redmill.models.Item(name=u"foo")
        self.session.add(foo)
        self.session.commit()

        bar = redmill.models.Item(name=u"bar", parent_id=foo.id)
        self.session.add(bar)
        self.session.commit()

        self.assertEqual(bar.parent_id, foo.id)

        self.assertEqual(foo.children, [bar])

    def test_parents(self):
        foo = redmill.models.Item(name=u"foo")
        self.session.add(foo)
        self.session.commit()

        bar = redmill.models.Item(name=u"bar", parent_id=foo.id)
        self.session.add(bar)
        self.session.commit()

        baz = redmill.models.Item(name=u"baz", parent_id=bar.id)
        self.session.add(baz)
        self.session.commit()

        self.assertEqual(baz.parents, [foo, bar])


if __name__ == "__main__":
    unittest.main()

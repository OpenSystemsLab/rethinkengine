from rethinkengine import Document

import rethinkdb as r
import unittest2 as unittest


class Test(Document):
    pass
    __primary_key__ = 'foo'


class MetaTestCase(unittest.TestCase):
    def setUp(self):
        self._drop()
        Test.table_create()

    def tearDown(self):
        self._drop()

    def _drop(self):
        try:
            Test.table_drop()
        except r.RqlRuntimeError:
            pass

    def test_primary_key_field(self):
        t = Test()
        t.save()
        obj = Test.objects.all()[0]
        self.assertTrue(hasattr(obj, 'id'))
        self.assertIn('foo', obj._doc)

    def test_primary_key_filter(self):
        # Assert whether we can filter by pk, even if we have set
        # primary_key_field to something else
        t = Test()
        t.save()
        pk = t.id

        # Should not raise error
        Test.objects.filter(id=pk)

    def test_table_name(self):
        class Test_TABLE_123(Document):
            pass
        self.assertEqual(Test_TABLE_123.__table_name__, 'test_table_123s')

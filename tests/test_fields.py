from rethinkengine.fields import *

import unittest2 as unittest


class PrimaryKeyFieldTestCase(unittest.TestCase):
    def test_default(self):
        f = PrimaryKeyField()
        self.assertEqual(f._default, None)

    def test_is_valid(self):
        f = PrimaryKeyField()
        self.assertTrue(f.is_valid('cdc14784-3327-492b-a1db-ad8a3b8abcef'))

    def test_too_short(self):
        f = PrimaryKeyField()
        self.assertFalse(f.is_valid('cdc14784-3327-492b-a1db-ad8a3b8abce'))

    def test_too_long(self):
        f = PrimaryKeyField()
        self.assertFalse(f.is_valid('cdc14784-3327-492b-a1db-ad8a3b8abcefa'))

    def test_wrong_chars(self):
        f = PrimaryKeyField()
        self.assertFalse(f.is_valid('zzzzzzzz-3327-492b-a1db-ad8a3b8abcef'))

    def test_wrong_type(self):
        f = PrimaryKeyField()
        self.assertFalse(f.is_valid(123))


class StringFieldTestCase(unittest.TestCase):
    def test_default(self):
        f = StringField()
        self.assertEqual(f._default, '')

    def test_is_valid(self):
        f = StringField()
        self.assertTrue(f.is_valid('foo'))
        self.assertTrue(f.is_valid(''))

    def test_wrong_type(self):
        f = StringField()
        self.assertFalse(f.is_valid(123))


class IntegerFieldTestCase(unittest.TestCase):
    def test_default(self):
        f = IntegerField()
        self.assertEqual(f._default, 0)

    def test_is_valid(self):
        f = IntegerField()
        self.assertTrue(f.is_valid(123))

    def test_wrong_type(self):
        f = IntegerField()
        self.assertFalse(f.is_valid('foo'))


class FloatFieldTestCase(unittest.TestCase):
    def test_default(self):
        f = FloatField()
        self.assertEqual(f._default, 0.)

    def test_is_valid(self):
        f = FloatField()
        self.assertTrue(f.is_valid(123.456))

    def test_wrong_type(self):
        f = FloatField()
        self.assertFalse(f.is_valid('foo'))
        self.assertFalse(f.is_valid(0))


class ListFieldTestCase(unittest.TestCase):
    def test_default(self):
        f = ListField()
        self.assertEqual(f._default, [])

    def test_is_valid(self):
        f = ListField()
        self.assertTrue(f.is_valid([1, 2, 3]))

    def test_wrong_type(self):
        f = ListField()
        self.assertFalse(f.is_valid('foo'))


class DictFieldTestCase(unittest.TestCase):
    def test_default(self):
        f = DictField()
        self.assertEqual(f._default, {})

    def test_is_valid(self):
        f = DictField()
        self.assertTrue(f.is_valid({}))
        self.assertTrue(f.is_valid({'foo': 1, 'bar': 2}))

    def test_wrong_type(self):
        f = DictField()
        self.assertFalse(f.is_valid('foo'))


class BooleanFieldTestCase(unittest.TestCase):
    def test_default(self):
        f = BooleanField()
        self.assertEqual(f._default, None)

    def test_is_valid(self):
        f = BooleanField()
        self.assertTrue(f.is_valid(False))
        self.assertTrue(f.is_valid(True))

    def test_none(self):
        f = BooleanField()
        self.assertFalse(f.is_valid(None))

    def test_wrong_type(self):
        f = BooleanField()
        self.assertFalse(f.is_valid('foo'))

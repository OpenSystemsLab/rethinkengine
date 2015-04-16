from .. import Foo
from rethinkengine.connection import connect, disconnect, ConnectionError
import rethinkdb as r
import unittest2 as unittest
from rethinkengine.document import Document
from rethinkengine.fields import *


class MyUser(Document):
    first_name = StringField(required=False)
    last_name = StringField(required=False)
    roles = ListField()
    age = IntegerField(required=False)

class CreateIndexTestCase(unittest.TestCase):
    def setUp(self):
        connect("test")
        MyUser.table_create()

        MyUser(first_name="First 1", last_name="Last", roles=["Developer", "System Administrator"], age=30).save()
        MyUser(first_name="First 2", last_name="Last", roles=["Developer", "System Administrator"], age=31).save()

    def tearDown(self):
        MyUser.table_drop()
        pass

    def test_create_index(self):
        MyUser.index_create("last_name")
        MyUser.index_wait("last_name")

        assert 2 == len(MyUser.get_all("Last", index="last_name"))

        MyUser.index_create("full_name", ["first_name", "last_name"])
        MyUser.index_wait("full_name")

        assert 1 == len(MyUser.get_all(["First 1", "Last"], index="full_name"))

        MyUser.index_create("roles", mutil=True)
        MyUser.index_wait("roles")
        assert 2 == len(MyUser.get_all("Developer", index="roles"))

        assert 3 == len(MyUser.index_list())



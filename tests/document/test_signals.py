from rethinkengine.connection import connect
import unittest2 as unittest
from rethinkengine.document import Document
from rethinkengine.fields import *
from rethinkengine.signals import Signaling


class User(Document, Signaling):
    class Meta:
        table_name = "signaling_users"

    first_name = StringField(required=False)
    last_name = StringField(required=False)
    roles = ListField()
    age = IntegerField(required=False)


@User.on_pre_save
def user_pre_save(document):
    document.first_name = document.first_name.upper()


@User.on_post_save
def user_post_save(document):
    document.age = 40


@User.on_pre_update
def user_pre_update(document):
    document.age = 35


@User.on_post_update
def user_post_update(document):
    document.roles.append("System Administrator")


@User.on_pre_delete
def user_pre_delete(document):
    document.age = -1


@User.on_post_delete
def user_post_delete(document):
    document.roles = []


class SignalingTestCase(unittest.TestCase):
    def setUp(self):
        connect("test")
        User.table_create()

    def tearDown(self):
        User.table_drop()
        pass

    def test_signaling(self):
        u1 = User(first_name="John", last_name="Doe", roles=["Developer"], age=30)
        first_name = u1.first_name
        u1.save()  # save

        assert u1.first_name == first_name.upper()
        assert u1.age == 40
        u1.save()  # update
        assert u1.age == 35
        assert len(u1.roles) == 2

        u1.delete()
        assert u1.age < 0
        assert len(u1.roles) == 0

if __name__ == "__main__":
    connect("test")
    User.table_create()

    u1 = User(first_name="John", last_name="Doe", roles=["Developer"], age=30)
    first_name = u1.first_name
    u1.save()  # save

    assert u1.first_name == first_name.upper()
    assert u1.age == 40
    u1.save()  # update
    assert u1.age == 35
    assert len(u1.roles) == 2

    u1.delete()
    assert u1.age < 0
    assert len(u1.roles) == 0


    User.table_drop()
import pytz
import datetime
from inflector import Inflector

from collections import OrderedDict

from rethinkengine.connection import get_conn
from rethinkengine.fields import BaseField, ObjectIdField, ReferenceField
from rethinkengine.query_set import QuerySetManager
from rethinkengine.errors import DoesNotExist, \
    MultipleObjectsReturned, RqlOperationError, ValidationError

import inspect
import rethinkdb as r

__all__ = ['BaseDocument', 'Document']

class BaseDocument(type):
    def __new__(mcs, name, bases, attrs):
        new_class = super(BaseDocument, mcs).__new__(mcs, name, bases, attrs)

        # If new_class is of type Document, return straight away
        if object in new_class.__bases__:
            return new_class

        # Process schema
        fields = sorted(
            inspect.getmembers(
                new_class,
                lambda o: isinstance(o, BaseField)
            ),
            key=lambda i: i[1]._creation_order)
        new_class._fields = attrs.get('_fields', OrderedDict())
        new_class._fields['id'] = ObjectIdField()
        for field_name, field in fields:
            new_class._fields[field_name] = field
            delattr(new_class, field_name)
        new_class.objects = QuerySetManager()

        # Merge exceptions
        classes_to_merge = (DoesNotExist, MultipleObjectsReturned)
        for c in classes_to_merge:
            exc = type(c.__name__, (c,), {'__module__': name})
            setattr(new_class, c.__name__, exc)

        # Populate table_name if not privided
        if new_class.__table_name__ is None:
            new_class.__table_name__ = Inflector().pluralize(name).lower()
        return new_class


class Document(object):
    __metaclass__ = BaseDocument
    
    __table_name__ = None
    __primary_key__ = 'id'
    __order_by__ = None

    def __init__(self, **kwargs):
        super(Document, self).__init__()
        self.__dict__['_data'] = {}
        self.__dict__['_iter'] = None
        self.__dict__['_dirty'] = True
        for name, value in kwargs.items():
            setattr(self, name, value)

    def __setattr__(self, key, value):
        field = self._fields.get(key, None)
        if field is not None:
            #Fix timezone for datetime
            if isinstance(value, datetime.datetime) and not value.tzinfo:
                value = pytz.utc.localize(value)
            if self._get_value(key) != value:
                self._dirty = True
            #Add _id if field if ReferenceField
            if isinstance(self._fields.get(key), ReferenceField):
                key += '_id'
            self._data[key] = value
        super(Document, self).__setattr__(key, value)

    def __getattr__(self, key):
        field = self._fields.get(key)
        if field:
            return self._get_value(key)
        raise AttributeError

    def __str__(self):
        return '<%s object>' % self.__class__.__name__

    def __iter__(self):
        return self

    def next(self):
        if not self._iter:
            self.__dict__['_iter'] = iter(self._fields)
        return self._iter.next()

    def __repr__(self):
        return '<%s object>' % self.__class__.__name__

    def items(self):
        return [(k, self._get_value(k)) for k in self._fields]

    @classmethod
    def index_create(cls, name, fields=None, mutil=False):

        if fields is None:
            fields = []
        if mutil is None:
            mutil = False

        table = r.table(cls.__table_name__)
        if len(fields) is 0 and not mutil:
            return table.index_create(name).run(get_conn())

        if len(fields) > 0:
            return table.index_create(name, [r.row[x] for x in fields]).run(get_conn())

        if mutil:
            return table.index_create(name, multi=True).run(get_conn())

        return False

    @classmethod
    def index_drop(cls, name):
        return r.table(cls.__table_name__).index_drop(name).run(get_conn())

    @classmethod
    def index_list(cls):
        return r.table(cls.__table_name__).index_list().run(get_conn())

    @classmethod
    def index_wait(cls, name):
        return r.table(cls.__table_name__).index_wait(name).run(get_conn())

    @classmethod
    def index_status(cls, name):
        return r.table(cls.__table_name__).index_status(name).run(get_conn())

    @classmethod
    def table_create(cls, if_not_exists=True):
        if (
            if_not_exists and
            (cls.__table_name__ in r.table_list().run(get_conn()))
        ):
            return

        return r.table_create(
            cls.__table_name__,
            primary_key=cls.__primary_key__
        ).run(get_conn())

    @classmethod
    def table_drop(cls):
        return r.table_drop(cls.__table_name__).run(get_conn())

    def validate(self):
        data = [(name, field, getattr(self, name)) for name, field in
                self._fields.items()]
        for name, field, value in data:
            if isinstance(field, ObjectIdField) and value is None:
                continue

            if not field.is_valid(value):
                raise ValidationError('Field %s: %s is of wrong type %s' %
                                      (name, field.__class__.__name__, type(value)))
    @classmethod
    def get_all(cls, *args, **kwargs):
        result = r.table(cls.__table_name__).get_all(*args, **kwargs).run(get_conn())
        return [cls(**o) for o in result]

    def save(self):
        if not self._dirty:
            return True
        self.validate()

        is_update = False
        try:
            if self.id:
                is_update = True
                self._pre_update()
            else:
                self._pre_save()
        except AttributeError:
            pass

        doc = self._doc
        table = r.table(self.__table_name__)

        if is_update:
            # TODO: implement atomic updates instead of updating entire doc
            result = table.get(self.id).update(doc).run(get_conn())
        else:
            result = table.insert(doc).run(get_conn())

        if result.get('errors', False) == 1:
            raise RqlOperationError(result['first_error'])

        self._dirty = False
        if 'generated_keys' in result:
            self._data['id'] = result['generated_keys'][0]

        try:
            if is_update:
                self._post_update()
            else:
                self._post_save()
        except AttributeError:
            pass

        return True

    def delete(self):
        table = r.table(self.__table_name__)
        if self._get_value('id'):
            try:
                self._pre_delete()
            except AttributeError:
                pass
            result = table.get(self._get_value('id')).delete().run(get_conn())
            try:
                self._post_delete()
            except AttributeError:
                pass

            return result

    def _get_value(self, field_name):
        key = field_name
        if isinstance(self._fields[field_name], ReferenceField):
            key += '_id'
        return self._data.get(key) or self._fields[field_name]._default

    def _to_python(self, field_name, value):
        if field_name in self._fields:
            return self._fields[field_name].to_python(value)
        else:
            return value

    def _to_rethink(self, field_name, value):
        if field_name in self._fields:
            return self._fields[field_name].to_rethink(value)
        else:
            return value

    @property
    def _doc(self):
        doc = {}
        for name, field_obj in self._fields.items():
            key = self.__primary_key__ if name == 'id' else name
            value = self._get_value(name)
            if key == self.__primary_key__ and value is None:
                continue
            if isinstance(field_obj, ReferenceField):
                key += '_id'

            doc[key] = None if not value else field_obj.to_rethink(value)

        return doc

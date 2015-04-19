import re
import datetime
import pytz

__all__ = ['BaseField', 'ObjectIdField', 'StringField',
           'IntegerField', 'FloatField', 'ListField',
           'DictField', 'BooleanField', 'DateField',
           'DateTimeField', 'ReferenceField']


class BaseField(object):
    _creation_counter = 0

    def __init__(self, required=False, default=None, **kwargs):
        self._creation_order = self._creation_counter
        BaseField._creation_counter += 1
        self._required = required
        self._default = default

    def __repr__(self):
        return '<%s object>' % self.__class__.__name__

    def to_python(self, value):
        return value

    def to_rethink(self, value):
        return self.to_python(value)

    def is_valid(self, value):
        if not self._required and value is None:
            return True
        return False


class ObjectIdField(BaseField):
    rx = r'^[0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}$'

    def __init__(self):
        # PrimaryKeyField.__init__ doesn't accept any arguments
        self._default = None

    def is_valid(self, value):
        return isinstance(value, basestring) and bool(re.match(self.rx, value))


class StringField(BaseField):
    def is_valid(self, value):
        if super(StringField, self).is_valid(value) is True:
            return True
        return isinstance(value, basestring)


class IntegerField(BaseField):
    def is_valid(self, value):
        if super(IntegerField, self).is_valid(value) is True:
            return True
        return isinstance(value, (int, long))


class FloatField(BaseField):
    def is_valid(self, value):
        if super(FloatField, self).is_valid(value) is True:
            return True
        return isinstance(value, (float))


class ListField(BaseField):
    _element_type = None

    def __init__(self, element_type=None, **kwargs):
        super(ListField, self).__init__(**kwargs)
        if element_type:
            if issubclass(element_type, BaseField):
                self._element_type = element_type
            else:
                raise TypeError('element_type must be instance of BaseField')

    def is_valid(self, value):
        if super(ListField, self).is_valid(value) is True:
            return True
        valid = isinstance(value, (list, tuple))
        if not valid:
            return False
        if self._element_type:
            for elem in value:
                if not self._element_type().is_valid(elem):
                    return False
        return True

    def to_python(self, value):
        return value or []


class DictField(BaseField):
    def is_valid(self, value):
        if super(DictField, self).is_valid(value) is True:
            return True
        return isinstance(value, dict)

    def to_python(self, value):
        return value or {}


class BooleanField(BaseField):
    def is_valid(self, value):
        if super(BooleanField, self).is_valid(value) is True:
            return True
        return isinstance(value, bool)


class DateField(BaseField):
    def to_python(self, value):
        if isinstance(value, basestring):
            year, month, day = value.split('-')
            return datetime.date(int(year), int(month), int(day))
        else:
            return value

    def to_rethink(self, value):
        if isinstance(value, datetime.date):
            return value.strftime('%Y-%m-%d')
        else:
            return None

    def is_valid(self, value):
        return (value is None) or (isinstance(value, datetime.date))


class DateTimeField(BaseField):
    def is_valid(self, value):
        return (value is None) or (isinstance(value, datetime.datetime))

    def to_rethink(self, value):
        if isinstance(value, datetime.datetime):
            if not value.tzinfo:
                value = pytz.utc.localize(value)
            return value
        else:
            return None


class ReferenceField(BaseField):

    def __init__(self, document_type, **kwargs):
        #TODO: Need param document_type is string
        from document import Document
        if not issubclass(document_type, Document):
                raise ValueError('Argument to ReferenceField constructor must be a '
                                 'Document class')
        self.document_type = document_type
        super(ReferenceField, self).__init__(**kwargs)

    def is_valid(self, value):
        flag = True
        if self._required and value is None:
            flag = False
        return flag

    def to_python(self, value):
        from document import Document
        return value if issubclass(type(value), Document) else self.document_type.objects.get(id=value)

    def to_rethink(self, value):
        from document import Document
        if issubclass(type(value), Document):
            return value.id
        elif value:
            return value
        else:
            return None
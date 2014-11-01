__all__ = ['ConnectionError', 'ValidationError', 'RqlOperationError', 'InvalidQueryError', 'MultipleObjectsReturned']


class ConnectionError(Exception):
    pass


class ValidationError(Exception):
    pass


class RqlOperationError(Exception):
    pass


class InvalidQueryError(Exception):
    pass


class MultipleObjectsReturned(Exception):
    pass


class DoesNotExist(Exception):
    pass


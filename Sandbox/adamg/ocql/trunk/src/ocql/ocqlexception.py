# -*- coding: UTF-8 -*-

from zope.interface import implements
from ocql.interfaces import IOCQLException

class OCQLException(Exception):
    implements(IOCQLException)

    def __init__(self, message):
        self.message = message

    def getMessage(self):
        return self.message
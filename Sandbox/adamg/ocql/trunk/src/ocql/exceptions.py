# -*- coding: UTF-8 -*-

from zope.interface import implements
from ocql.interfaces import IOCQLException
from ocql.interfaces import IReanalyzeRequired

class OCQLException(Exception):
    implements(IOCQLException)

    def __init__(self, message=None):
        self.message = message

    def getMessage(self):
        return self.message

class ReanalyzeRequired(OCQLException):
    implements(IReanalyzeRequired)

# vim:fileencoding=utf-8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Unit test support."""

import tempfile

import ZODB.utils
import ZODB.config
import ZODB.FileStorage


class Opener(ZODB.config.BaseConfig):

    def open(self):
        return FailingStorage(self.name)


def failing_method(name):
    """Produces a method that can be made to fail."""
    def fail(self, *args, **kw):
        if name == self._fail:
            raise Exception()
        return getattr(ZODB.FileStorage.FileStorage, name)(self, *args, **kw)
    return fail


class FailingStorage(ZODB.FileStorage.FileStorage):

    _fail = None

    def __init__(self, name):
        self.name = name
        file_handle, file_name = tempfile.mkstemp()
        ZODB.FileStorage.FileStorage.__init__(self, file_name)

    def close(self):
        ZODB.FileStorage.FileStorage.close(self)
        self.cleanup()

    def getExtensionMethods(self):
        return dict(fail=None)

    history = failing_method('history')
    loadSerial = failing_method('loadSerial')

    def fail(self, method_name):
        if method_name in ['history', 'loadSerial']:
            # Those methods are copied/references by the server code, we can't
            # rebind them here.
            self._fail = method_name
            return

        old_method = getattr(self, method_name)
        def failing_method(*args, **kw):
            setattr(self, method_name, old_method)
            raise Exception()
        setattr(self, method_name, failing_method)

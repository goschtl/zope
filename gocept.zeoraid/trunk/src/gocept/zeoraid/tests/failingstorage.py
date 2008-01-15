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

    def history(self, *args, **kw):
        if 'history' == self._fail:
            raise Exception()
        return ZODB.FileStorage.FileStorage.history(self, *args, **kw)

    def fail(self, method):
        if method in ['history']:
            # Those methods are copied/references by the server code, we can't
            # rebind them here.
            self._fail = method
            return

        old_method = getattr(self, method)
        def failing_method(*args, **kw):
            setattr(self, method, old_method)
            raise Exception()
        setattr(self, method, failing_method)

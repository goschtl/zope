# vim:fileencoding=utf-8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Unit test support."""

import ZODB.utils
import ZODB.config
import ZODB.MappingStorage


class Opener(ZODB.config.BaseConfig):

    def open(self):
        return FailingStorage(self.name)


class FailingStorage(ZODB.MappingStorage.MappingStorage):

    def getExtensionMethods(self):
        return dict(fail=None)

    def fail(self, method):
        old_method = getattr(self, method)
        def failing_method(*args, **kw):
            setattr(self, method, old_method)
            raise Exception()
        setattr(self, method, failing_method)

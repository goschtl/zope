##############################################################################
#
# Copyright (c) 2006 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Source that uses the policies from the source factory.

"""
__docformat__ = "reStructuredText"


import zope.interface
import zope.schema.interfaces

import zc.sourcefactory.interfaces


class FactoredSource(object):
    """An iterable source that was created from a source factory."""

    zope.interface.implements(zc.sourcefactory.interfaces.IFactoredSource)

    def __init__(self, factory):
        self.factory = factory

    def __iter__(self):
        return self._get_filtered_values()

    def __len__(self):
        # This is potentially expensive!
        return len(list(self._get_filtered_values()))

    def __contains__(self, value):
        return value in self._get_filtered_values()

    def _get_filtered_values(self):
        for value in self.factory.getValues():
            if not self.factory.filterValue(value):
                continue
            yield value


class FactoredContextualSource(FactoredSource):
    """An iterable context-aware source that was created from a source factory.
    """

    zope.interface.implements(zc.sourcefactory.interfaces.IContextualSource)

    def __init__(self, factory, context):
        self.factory = factory
        self.context = context
        self.__parent__ = context

    def _get_filtered_values(self):
        for value in self.factory.getValues(self.context):
            if not self.factory.filterValue(self.context, value):
                continue
            yield value

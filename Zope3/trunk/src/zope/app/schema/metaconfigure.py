##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""ZCML special vocabulary directive handlers

$Id: metaconfigure.py,v 1.1 2003/08/01 21:48:34 srichter Exp $
"""
import zope.app.schema.vocabulary

__metaclass__ = type


class FactoryKeywordPasser:
    """Helper that passes additional keywords to the actual factory."""

    def __init__(self, factory, kwargs):
        self.factory = factory
        self.kwargs = kwargs

    def __call__(self, object):
        return self.factory(object, **self.kwargs)


def vocabulary(_context, name, factory, **kw):
    service = zope.app.schema.vocabulary.vocabularyService
    if kw:
        factory = FactoryKeywordPasser(factory, kw)
    _context.action(
        discriminator=('defineVocabulary', name),
        callable=service.register,
        args=(name, factory) )


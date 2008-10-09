##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" installer for z3ext.poduct

$Id: product.py 860 2008-01-09 08:48:08Z fafhrd91 $
"""
from zope import interface
from zope.app.catalog.interfaces import ICatalogIndex

from z3ext.product.utils import registerUtility, unregisterUtility

from z3ext.lucene.i18n import _
from z3ext.lucene.interfaces import ILuceneIndex, ILuceneProduct

from z3ext.lucene.index import BaseLuceneTextIndex


class PortalLuceneIndex(BaseLuceneTextIndex):
    """ portal index """


class LuceneInstaller(object):
    interface.implements(ILuceneProduct)

    def update(self):
        registerUtility('z3ext.lucene', PortalLuceneIndex,
                        ((ILuceneIndex, ''), 
                         (ICatalogIndex, 'searchableText')))
        super(LuceneInstaller, self).update()

    def uninstall(self):
        unregisterUtility('z3ext.lucene',
                          ((ILuceneIndex, ''), (ICatalogIndex, 'searchableText')))
        super(LuceneInstaller, self).uninstall()

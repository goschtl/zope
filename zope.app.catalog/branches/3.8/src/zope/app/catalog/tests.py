##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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
"""Tests for backward-compatibility imports

$Id: tests.py 95860 2009-02-01 15:55:13Z nadako $
"""
import unittest
from zope.testing import doctest

def test_imports():
    '''
    Here, we test if old import places are still available and we
    got what we need by importing from them.
    
    >>> from zope.app.catalog.attribute import AttributeIndex
    >>> AttributeIndex
    <class 'zope.catalog.attribute.AttributeIndex'>

    >>> from zope.app.catalog.catalog import (
    ...     ResultSet,
    ...     Catalog,
    ...     indexAdded,
    ...     indexDocSubscriber,
    ...     reindexDocSubscriber,
    ...     unindexDocSubscriber,
    ... )
    >>> ResultSet
    <class zope.catalog.catalog.ResultSet at 0x...>
    >>> Catalog
    <class 'zope.catalog.catalog.Catalog'>
    >>> indexAdded
    <function indexAdded at 0x...>
    >>> indexDocSubscriber
    <function indexDocSubscriber at 0x...>
    >>> reindexDocSubscriber
    <function reindexDocSubscriber at 0x...>
    >>> unindexDocSubscriber
    <function unindexDocSubscriber at 0x...>

    >>> from zope.app.catalog.field import IFieldIndex, FieldIndex
    >>> IFieldIndex
    <InterfaceClass zope.catalog.field.IFieldIndex>
    >>> FieldIndex
    <class 'zope.catalog.field.FieldIndex'>

    >>> from zope.app.catalog.interfaces import (
    ...     ICatalogQuery,
    ...     ICatalogEdit,
    ...     ICatalogIndex,
    ...     ICatalog,
    ...     IAttributeIndex,
    ...     INoAutoIndex,
    ...     INoAutoReindex,
    ... )
    >>> ICatalogQuery
    <InterfaceClass zope.catalog.interfaces.ICatalogQuery>
    >>> ICatalogEdit
    <InterfaceClass zope.catalog.interfaces.ICatalogEdit>
    >>> ICatalogIndex
    <InterfaceClass zope.catalog.interfaces.ICatalogIndex>
    >>> ICatalog
    <InterfaceClass zope.catalog.interfaces.ICatalog>
    >>> IAttributeIndex
    <InterfaceClass zope.catalog.interfaces.IAttributeIndex>
    >>> INoAutoIndex
    <InterfaceClass zope.catalog.interfaces.INoAutoIndex>
    >>> INoAutoReindex
    <InterfaceClass zope.catalog.interfaces.INoAutoReindex>
    
    >>> from zope.app.catalog.keyword import (
    ...     IKeywordIndex,
    ...     KeywordIndex,
    ...     CaseInsensitiveKeywordIndex,
    ... )
    >>> IKeywordIndex
    <InterfaceClass zope.catalog.keyword.IKeywordIndex>
    >>> KeywordIndex
    <class 'zope.catalog.keyword.KeywordIndex'>
    >>> CaseInsensitiveKeywordIndex
    <class 'zope.catalog.keyword.CaseInsensitiveKeywordIndex'>

    >>> from zope.app.catalog.text import ITextIndex, TextIndex
    >>> ITextIndex
    <InterfaceClass zope.catalog.text.ITextIndex>
    >>> TextIndex
    <class 'zope.catalog.text.TextIndex'>
    '''

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(optionflags=doctest.ELLIPSIS))
    return suite

if __name__ == "__main__":
    unittest.main()

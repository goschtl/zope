##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""PageletChooser vocabulary

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import directlyProvides

from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from zope.app import zapi

from zope.app.component.interface import queryInterface

from zope.app.pagelet.interfaces import IPagelet

from zope.app.pageletchooser.exceptions import \
    PageletVocabularyInterfaceLookupError
from zope.app.pageletchooser.exceptions import \
    PageletError_vocabulary_interface_not_found

from zope.app.pageletchooser.interfaces import IChooseablePagelets



class Wrapper:
    """Dummy class for to provide a interface."""



class PageletNamesVocabulary(SimpleVocabulary):
    """A vocabular of optional pagelet macro names for a given interface.

    Imports:
    
        >>> from zope.interface import Interface
        >>> from zope.security.checker import defineChecker
        >>> from zope.publisher.interfaces.browser import IBrowserRequest
        >>> from zope.component.interfaces import IView
        >>> from zope.app.pagelet.interfaces import IPagelet
        >>> from zope.app.pagelet.interfaces import IPageletSlot
        >>> from zope.app.pagelet.tests import TestPagelet
        >>> from zope.app.pagelet.tests import TestContext
        >>> from zope.app.pagelet.tests import testChecker

    Setup:

        >>> from zope.app.testing import setup, ztapi
        >>> setup.placefulSetUp()

    Register interfaces used for pagelet and vocabulary:

        >>> from zope.app.component.interface import provideInterface
        >>> provideInterface('', IBrowserRequest, None)
        >>> provideInterface('', IView, None)
        >>> provideInterface('', IChooseablePagelets, None)

    Register pagelet:

        >>> name = 'testpagelet'
        >>> pagelet_factory = TestPagelet
        >>> defineChecker(pagelet_factory, testChecker)
        >>> gsm = zapi.getGlobalSiteManager()
        >>> gsm.provideAdapter(
        ...        (Interface, IBrowserRequest, IView, IPageletSlot)
        ...        , IPagelet, name, pagelet_factory)

    Register vocabulary:
        
        >>> from zope.app.pagelet.tests import TestContext
        >>> name='chooseablepageletnames'
        >>> factory='.vocabulary.PageletNamesVocabulary'
        >>> layer='zope.publisher.interfaces.browser.IBrowserRequest'
        >>> view='zope.component.bbb.interfaces.IView'
        >>> slot='zope.app.pageletchooser.interfaces.IChooseablePagelets'
        >>> obj = TestContext()
        >>> vocab = PageletNamesVocabulary(obj, layer, view, slot)

    Test vocabulary:

        >>> 'testpagelet' in vocab
        True

        >>> 'nothing' in vocab
        False

        >>> setup.placefulTearDown()

    """
    def __init__(self, context, layer, view, slot):
        macronames = []
        terms = []
        
        # get and check interface
        layeriface = queryInterface(layer)
        if layeriface is None:
            raise PageletVocabularyInterfaceLookupError(
                    PageletError_vocabulary_interface_not_found, layer)

        viewiface = queryInterface(view)
        if viewiface is None:
            raise PageletVocabularyInterfaceLookupError(
                    PageletError_vocabulary_interface_not_found, view)

        slotiface = queryInterface(slot)
        if slotiface is None:
            raise PageletVocabularyInterfaceLookupError(
                    PageletError_vocabulary_interface_not_found, slot)

        # prepare objects for lookup the adapters        
        layerwrapper = Wrapper()
        directlyProvides(layerwrapper, layeriface)
        
        viewwrapper = Wrapper()
        directlyProvides(viewwrapper, viewiface)
        
        slotwrapper = Wrapper()
        directlyProvides(slotwrapper, slotiface)
        
        # collect pagelets
        objects = context, layerwrapper, viewwrapper, slotwrapper
        pagelets = zapi.getAdapters(objects, IPagelet)
        pagelets.sort(lambda x, y: x[1].weight - y[1].weight)

        for name, pagelet in pagelets:
            macronames.append(name)

        for name in macronames:
            terms.append(SimpleTerm(name, name, name))

        terms.sort(lambda lhs, rhs: cmp(lhs.title, rhs.title))
        super(PageletNamesVocabulary, self).__init__(terms)

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
"""Pagelet interfaces

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.tales.interfaces import ITALESExpression

from zope.interface import Interface
from zope.interface import Attribute
from zope.schema import Int

from zope.app.i18n import ZopeMessageIDFactory as _
        


class IPageletSlot(Interface):
    """Marker interface for pagelet slots.
    
    The pagelet slot is used as a part ot the key for to register and 
    collect pagelets.
    """



class IPagelet(Interface):
    """Interface for custom pagelet adapters.
    
    Pagelets can be used in a page template as a piece of content
    rendered with it's own python view class. Yes with pagelets
    you can use more then one views in a pageltemplate. This
    let's pagelets act as portlets. The pagelet view can support
    content independent information where you can access in every
    page template on which the pagelet is registred.
    
    The meta directive set the 'weight' attribute to the class attribute
    '_weight'. If you whould like to use the settings from the meta 
    directive point the attribute 'weight' to this default attribute.
    
    If you use a 'template', the meta directive sets the 'template' to 
    the class attribute '_template'.
    """

    weight = Int(
        title=_(u'weight'),
        description=_(u"""
            Key for sorting pagelets if the pagelet collector is supporting
            this sort mechanism."""),
        required=False,
        default=0)

    def __getitem__(name):
        """Returns the macro code of the template by the given name."""



class IPageData(Interface):
    """Base interface for custom page data adapters."""




class IMacrosCollector(Interface):
    """Lookup pagelets from the TALES directive 'pagelets:'.
    
    A adpater providing this interface is called in:
    pagelet.tales.TALESPageletsExpression via the TALES expression 
    called tal:pagelets.
    
    If you like to use a layout manager for managing pagelets, implement
    your own pagelet collector which calls a layout manager.
    
    Remember: you can register your own pagelet collector on 
    layers, because there is a request in the adapter registration
    tuple. (Request provides the layer interface)
    """
    
    def macros():
        """Returns macros related to the context, request, view and slot.
        
        The pagelets are registred as adapters on a tuple like:
        
        (context, request, view, slot)
        
        where the attributes are:
        
        context -- the content object
        request -- the browser request providing a layer interface
        view -- the context view, normaly a browser page or view
        slot -- a slot wrapper instance providing the slot interface 
        """



class IMacroCollector(Interface):
    """Lookup a single pagelet from the TALES directive 'pagelet:'
    
    by the given interface.
    
    A adpater providing this interface is called in:
    pagelet.tales.TALESPageletsExpression via the TALES expression 
    called tal:pagelet.
    
    """
    
    def __getitem__(key):
        """Returns a single pagelet macro registred by the given name.
        
        The pagelets are registred as adapters on a tuple like:
        
        (context, request, view, slot)
        
        where the attributes are:
        
        context -- the content object
        request -- the browser request providing a layer interface
        view -- the context view, normaly a browser page or view
        slot -- a slot wrapper instance providing the slot interface 
        """



class ITALESPageletsExpression(ITALESExpression):
    """Tal namespace for getting a list of macros form a IMacrosCollector.
    
    For to call pagelets in a view use the the following syntax in 
    a page template:
    <metal:block 
     tal:repeat="pagelet pagelets:zope.app.demo.pagelet.interfaces.IDemoSlot">
        <tal:block metal:use-macro="pagelet" />
	</metal:block>
    where 'zope.app.pagelet.demo.interfaces.IDemoSlot' is a slot interface 
    wich implements pagelet.interfaces.IPageletSlot.
    """

    pagelets = Attribute("pagelets",
                _(u"Pagelets registred for context, request, view and slot."))



class ITALESPageletExpression(ITALESExpression):
    """Tal namespace for getting a IMacroCollector adapter.
    
    For to call pagelets in a view use the the following syntax in 
    a page template:
    <div class="row" 
         tal:define="collector global ...
                     ... pagelets:zope.app.pagelet.demo.interfaces.IDemoSlot">
      <tal:block metal:use-macro="collector/testpagelet" />
    </div>
    where 'zope.app.pagelet.demo.interfaces.IDemoSlot' is a slot interface wich
    implements pagelet.interfaces.IPageletSlot.
    """

    pagelet = Attribute("pagelet",
                _(u"Pagelet registred for context, request, view and slot."))



class ITALESPageDataExpression(ITALESExpression):
    """Tal namespace for set the view namespace in MacrosCollector.
    
    For to call a page data adapter in a page template use the the 
    following syntax:
    <metal:block 
        tal:define="data pagedata:x.y.interfaces.IDemoPageData" />
    where 'x.y.interfaces.IDemoPageData' is a portlet interface wich
    implements pagelet.interfaces.IPageData.
    """

    pagedata = Attribute("pagedata",
            _(u"Page data adapter registred for context, request and view."))

    def __call__():
        """Returns the page data adapter."""

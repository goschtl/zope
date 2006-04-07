##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""

$Id: __init__.py 41271 2006-01-11 17:02:07Z oestermeier $
"""
__docformat__ = 'restructuredtext'

import sys, unittest, doctest

import zope.interface
import zope.component

from zope.interface.advice import addClassAdvisor
from zope.dottedname.resolve import resolve

class ClassUsage(object) :
    """ Describes the usage of a class. """
    
    def __init__(self, klass) :
        self.klass = klass
    
class AdapterUsage(ClassUsage) :
    """ Describes the usage of a class as an adapter factory. """
    
    def __init__(self, klass, adapts=None, provides=None, name='') :
        self.klass = klass
        self.adapts = adapts
        self.provides = provides
        self.name = name
        
    def register(self) :
        """ Registers the adapter. """
        zope.component.provideAdapter(self.klass, 
                                            adapts=self.adapts,
                                            provides=self.provides,
                                            name=self.name)
        
class GlobalUtilityUsage(ClassUsage) :
    """ Describes the usage of a class as a factory for a global utility. """

    def register(self) :
        """ Registers the global utility. """


def _adapter(cls):
    
    adapts, provides, name = cls.__dict__['__adapter_usage_data__']
    del cls.__adapter_usage_data__
    
    if provides is None :
        provides = list(cls.__implemented__.interfaces())[0]
    else :
        classImplements(cls, iface)
        
    if adapts is None :
        adapts = zope.component.adaptedBy(cls)
    else :
        zope.component.adapter(adapts)(cls)
      
    if not hasattr(cls, '__zorg_usages__') :
        cls.__zorg_usages__ = []
        
    usage = AdapterUsage(cls, adapts=adapts, provides=provides, name=name)
    cls.__zorg_usages__.append(usage)
    return cls

def adapter(adapts=None, provides=None, name='') :
    """
    Declares the usage of a class as an adapter factory.
    
    >>> class IAdapted(zope.interface.Interface) :
    ...     pass
    >>> class IAdapter(zope.interface.Interface) :
    ...     pass
    
    class Adapter(object) :
    ...     zope.interface.implements(IAdapter)
    ...     zope.component.adapts(IAdapted)
    ...     adapter()
        
        
    
    """
    frame = sys._getframe(1)
    locals = frame.f_locals
    
    # Try to make sure we were called from a class def. In 2.2.0 we can't
    # check for __module__ since it doesn't seem to be added to the locals
    # until later on.
    if (locals is frame.f_globals) or ('__module__' not in locals):
        raise TypeError("provides can be used only from a class definition.")

    locals['__adapter_usage_data__'] =  adapts, provides, name
    addClassAdvisor(_adapter)
    
def globalUtility() :
    pass # to be written
    
def ensureRegistrations(dotted_name) :
    module = resolve(dotted_name)
    for key in dir(module) :
        obj = getattr(module, key)
        for usage in getattr(obj, "__zorg_usages__", ()) :
            usage.register()
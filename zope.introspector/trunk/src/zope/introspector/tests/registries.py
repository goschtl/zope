"""
Tests for the package internal adapters and utilities.

:Test-Layer: python

"""
import unittest

from zope.app.testing import placelesssetup, ztapi
from zope.app.zapi import getUtility

from zope.introspector.registry import RegistryInfoUtility
from zope.introspector.interfaces import IRegistryInfo, IRegistrySearch
from zope.introspector.adapters import *

from zope.interface import Interface, implements


class IDummy(Interface):
    """Just a dummy interface
    """

class Dummy(object):
    """ Just to implement IDummy
    """
    implements(IDummy)
    
class ComponentInterfaceRegisterTestCase(placelesssetup.PlacelessSetup,
                                         unittest.TestCase):
    
    def setUp(self):
        placelesssetup.setUp()
        ztapi.provideAdapter(IUtilityRegistration, IRegistrySearch,
                             UtilitySearch)
        ztapi.provideAdapter(IHandlerRegistration, IRegistrySearch,
                             HandlerSearch)
        ztapi.provideAdapter(IAdapterRegistration, IRegistrySearch,
                             AdapterSearch)

    
    def test_list_handlers(self):
        handlers = RegistryInfoUtility().getAllHandlers()
        self.failUnless(isinstance(handlers, list))
    
    def test_list_adapters(self):
        adapters = RegistryInfoUtility().getAllAdapters()
        self.failUnless(isinstance(adapters, list))
    
    def test_list_utilities(self):
        utilities = RegistryInfoUtility().getAllUtilities()
        self.failUnless(isinstance(utilities, list))
    
    def test_list_all_registrations(self):
        util = RegistryInfoUtility()
        result = util.getAllRegistrations()
        self.failUnless(isinstance(result, list))
        
    def test_interface_search(self):
        ztapi.provideUtility(IDummy, Dummy)
        result = RegistryInfoUtility().getRegistrationsForInterface(
            'Dummy', types=['utilities'])
        self.failUnless(len(result) == 1)
        
    def test_get_component_registry(self):
        interfaces = RegistryInfoUtility().getAllInterfaces()
        self.failUnless(isinstance(interfaces, dict))
        

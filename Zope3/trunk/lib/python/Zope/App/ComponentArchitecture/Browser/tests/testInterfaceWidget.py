##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Interface field widget tests

$Id: testInterfaceWidget.py,v 1.3 2002/12/21 19:50:29 stevea Exp $
"""

__metaclass__ = type

from Interface import Interface
from unittest import TestCase, TestSuite, main, makeSuite
from Zope.Testing.CleanUp import CleanUp
from Zope.App.ComponentArchitecture.InterfaceService import InterfaceService
from Zope.App.ComponentArchitecture.IInterfaceService import IInterfaceService
from Zope.App.ComponentArchitecture.InterfaceField \
     import InterfaceField
from Zope.App.ComponentArchitecture.Browser.InterfaceWidget \
     import SingleInterfaceWidget
from Zope.Publisher.Browser.BrowserRequest import TestRequest
from Zope.ComponentArchitecture.GlobalServiceManager \
     import serviceManager, defineService


class I(Interface):
    """bah blah
    """
    
class I2(Interface):
    """eek
    """
    
class I3(Interface):
    """
    """
    def one():
        """method one"""

    def two():
        """method two"""
        
class Test(CleanUp, TestCase):
    """Test Interface for InterfaceService Instance.
    """

    def testInterfaceWidget(self):
        service = InterfaceService()
        defineService('Interfaces', IInterfaceService)
        serviceManager.provideService('Interfaces', service)
        service.provideInterface(I.__module__+'.'+I.__name__, I)
        service.provideInterface(I2.__module__+'.'+I2.__name__, I2)
        service.provideInterface(I3.__module__+'.'+I3.__name__, I3)

        request = TestRequest()
        
        interfaceField = InterfaceField(__name__ = 'TestName',
                                        title = u"This is a test",
                                        required=False)
        
        widget = SingleInterfaceWidget(interfaceField, request)
        
        self.assertEqual(widget.getData(), None)
       
        out = (
        '<input type="text" name="field.TestName.search" value="">' 
        '<select name="field.TestName">' 
        '<option value="">---select interface---</option>'

        '<option value="'
        'Zope.App.ComponentArchitecture.Browser.tests.testInterfaceWidget.I'
        '">'
        'Zope.App.ComponentArchitecture.Browser.tests.testInterfaceWidget.I'
        '</option>' 

        '<option value="'
        'Zope.App.ComponentArchitecture.Browser.tests.testInterfaceWidget.I2'
        '">'
        'Zope.App.ComponentArchitecture.Browser.tests.testInterfaceWidget.I2'
        '</option>' 

        '<option value="'
        'Zope.App.ComponentArchitecture.Browser.tests.testInterfaceWidget.I3'
        '">'
        'Zope.App.ComponentArchitecture.Browser.tests.testInterfaceWidget.I3'
        '</option>' 

        '</select>'
        )
        
        self.assertEqual(widget(), out)
        
        out = (
        '<input type="text" name="field.TestName.search" value="">'
        '<select name="field.TestName">'
        '<option value="">---select interface---</option>'

        '<option value="'
        'Zope.App.ComponentArchitecture.Browser.tests.testInterfaceWidget.I'
        '" selected>'
        'Zope.App.ComponentArchitecture.Browser.tests.testInterfaceWidget.I'
        '</option>'

        '<option value="'
        'Zope.App.ComponentArchitecture.Browser.tests.testInterfaceWidget.I2'
        '">'
        'Zope.App.ComponentArchitecture.Browser.tests.testInterfaceWidget.I2'
        '</option>'

        '<option value="'
        'Zope.App.ComponentArchitecture.Browser.tests.testInterfaceWidget.I3'
        '">'
        'Zope.App.ComponentArchitecture.Browser.tests.testInterfaceWidget.I3'
        '</option>'

        '</select>'
        )
        
        self.assertEqual(widget.render(I), out)

        self.assertEqual(widget.getData(), None)

        widget = SingleInterfaceWidget(interfaceField, request)
        
        request.form["field.TestName"] = (
        'Zope.App.ComponentArchitecture.Browser.tests.testInterfaceWidget.I2'
        )
        self.assertEqual(widget.getData(), I2)

        out = (
        '<input type="text" name="field.TestName.search" value="">' 
        '<select name="field.TestName">' 

        '<option value="">---select interface---</option>'
        '<option value="'
        'Zope.App.ComponentArchitecture.Browser.tests.testInterfaceWidget.I'
        '">'
        'Zope.App.ComponentArchitecture.Browser.tests.testInterfaceWidget.I'
        '</option>' 

        '<option value="'
        'Zope.App.ComponentArchitecture.Browser.tests.testInterfaceWidget.I2'
        '" selected>'
        'Zope.App.ComponentArchitecture.Browser.tests.testInterfaceWidget.I2'
        '</option>' 

        '<option value="'
        'Zope.App.ComponentArchitecture.Browser.tests.testInterfaceWidget.I3'
        '">'
        'Zope.App.ComponentArchitecture.Browser.tests.testInterfaceWidget.I3'
        '</option>' 

        '</select>'
        )
        self.assertEqual(widget(), out)
                
        request.form["field.TestName.search"] = 'two'
        out = (
        '<input type="text" name="field.TestName.search" value="two">' 
        '<select name="field.TestName">' 
        '<option value="">---select interface---</option>'

        '<option value="'
        'Zope.App.ComponentArchitecture.Browser.tests.testInterfaceWidget.I3'
        '">'
        'Zope.App.ComponentArchitecture.Browser.tests.testInterfaceWidget.I3'
        '</option>' 

        '</select>'
        )
        self.assertEqual(widget(), out)

       
def test_suite():
    return TestSuite((makeSuite(Test),))



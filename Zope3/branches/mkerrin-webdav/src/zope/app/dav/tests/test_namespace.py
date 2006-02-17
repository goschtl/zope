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
"""Test the Zope WebDAV namespace registry.

$Id:$
"""
import unittest
from cStringIO import StringIO

from zope.configuration import xmlconfig
from zope.configuration.config import ConfigurationExecutionError
from zope.interface.interfaces import IInterface
from zope.interface.verify import verifyObject
from zope.interface import Interface, implements
import zope.app.dav.tests
from zope.app.component.testing import PlacefulSetup

from zope import component
from zope.interface.declarations import directlyProvides
from zope.schema import Int, TextLine
from zope.schema.interfaces import IInt, ITextLine
from zope.app.dav.namespaces import NamespaceManager
from zope.app.dav.interfaces import INamespaceManager, IWebDAVRequest, \
     IDAVWidget
from zope.app.dav.common import WebDAVRequest
from zope.app.dav.widget import IntDAVWidget, TextDAVWidget

namespace = 'http://examplenamespace.org/dav/schema'

#
# Some Schema's to test for properties.
#

class IExampleNamespaceType(IInterface):
    """ """

class IExampleSchema(Interface):
    """ """
    age = Int(title = u'Age')

    name = TextLine(title = u'Name')

class IExampleExtendedSchema(IExampleSchema):
    """ """
    job = TextLine(title = u'Job Title')

    company = TextLine(title = u'Place of employment')

class IExampleContactSchema(Interface):
    """ """
    phoneNo = TextLine(title = u'Phone Number')

class IExampleDuplicateSchema(Interface):
    """ """
    age = TextLine(title = u'Duplicate age property')

#
# Some interfaces and content objects and adapters to test the schemas against.
#

class IExampleContent(Interface):
    """Marker interface for content objects...
    """


class IExampleExtendedContent(IExampleContent):
    """Marker interface for content objects that will have the IExampleExtended
    properties defined on them.
    """


class IExampleContactContent(Interface):
    """Marker interface for content objects that have the IExampleContactSchema
    properties defined on them.
    """


class Content(object):
    implements(IExampleContent)

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__   = name


class ExampleAdapter(object):
    implements(IExampleSchema)

    def __init__(self, context):
        self.context = context

    @property
    def age(self):
        return 15

    @property
    def name(self):
        return 'The Other Michael Kerrin'

class ExampleExtendedAdapter(object):
    implements(IExampleExtendedSchema)

    def __init__(self, context):
        self.context = context

    @property
    def age(self):
        return 10

    @property
    def name(self):
        return 'Michael Kerrin'

    @property
    def job(self):
        return 'Programmer'

    @property
    def company(self):
        return 'OpenApp'


class ExampleContactAdapter(object):
    implements(IExampleContactSchema)

    def __init__(self, context):
        self.context = context

    @property
    def phoneNo(self):
        return '01 1234567'


class TestNamespaceDirectives(unittest.TestCase):

    def test_namespace_directives(self):
        self.assertEqual(
            component.queryUtility(INamespaceManager, namespace), None)
        xmlconfig.XMLConfig("davnamespace.zcml", zope.app.dav.tests)()
        nmanager = component.getUtility(INamespaceManager, namespace)
        verifyObject(INamespaceManager, nmanager)
        # quick check to see that schemas work
        self.assert_(len(nmanager.properties) > 0)
        # check that we correctly catch duplicate declarations of properties
        self.assertRaises(ConfigurationExecutionError,
                          xmlconfig.XMLConfig("davduplicateproperty.zcml",
                                              zope.app.dav.tests))


class TestNamespaceRegistry(unittest.TestCase):

    def setUp(self):
        davnamespace = NamespaceManager(namespace,
                                        schemas = (IExampleSchema,
                                                   IExampleExtendedSchema,
                                                   IExampleContactSchema))
        component.provideUtility(davnamespace, INamespaceManager, namespace)

        # all objects have the properties defined in IExampleSchema defined.
        component.provideAdapter(ExampleAdapter, (IExampleContent,),
                                 IExampleSchema)
        component.provideAdapter(ExampleExtendedAdapter,
                                 (IExampleExtendedContent,),
                                 IExampleExtendedSchema)
        component.provideAdapter(ExampleContactAdapter,
                                 (IExampleContactContent,),
                                 IExampleContactSchema)

        # setup for widget adapters.
        component.provideAdapter(IntDAVWidget, (IInt, IWebDAVRequest),
                                 IDAVWidget)
        component.provideAdapter(TextDAVWidget, (ITextLine, IWebDAVRequest),
                                 IDAVWidget)

    def test_correct_properties(self):
        nr = component.getUtility(INamespaceManager, namespace)
        expected = ['age', 'name', 'job', 'company', 'phoneNo']
        expected.sort()
        props = nr.properties.keys()
        props.sort()
        self.assertEqual(props, expected)

    def test_correct_schema(self):
        nr = component.getUtility(INamespaceManager, namespace)
        ageschema = nr.properties['age']
        jobschema = nr.properties['job']
        self.assertEqual(ageschema, IExampleSchema)
        self.assertEqual(jobschema, IExampleExtendedSchema)

    def test_defined_properties(self):
        # should be missing the phoneNo since no adapter exists.
        nr = component.getUtility(INamespaceManager, namespace)
        context = Content(None, 'contenttype')
        names = list(nr.getAllPropertyNames(context))
        names.sort()
        self.assertEquals(names, ['age', 'name'])
        # now extend the what the context object implements
        directlyProvides(context, (IExampleExtendedContent,
                                   IExampleContactContent))
        names = list(nr.getAllPropertyNames(context))
        names.sort()
        self.assertEquals(names, ['age', 'company', 'job', 'name', 'phoneNo'])

    def test_properties(self):
        nr = component.getUtility(INamespaceManager, namespace)
        context = Content(None, 'contenttype')
        directlyProvides(context, (IExampleExtendedContent,
                                   IExampleContactContent))
        fields = list(nr.getAllProperties(context))

        names  = [field.getName() for field in fields]
        names.sort()
        self.assertEquals(names, ['age', 'company', 'job', 'name', 'phoneNo'])

        #
        # Assert that the adapters found via the namespace manager matches
        # what we expect.
        #
        adapters = {'age': ExampleExtendedAdapter,
                    'company': ExampleExtendedAdapter,
                    'job': ExampleExtendedAdapter,
                    'name': ExampleExtendedAdapter,
                    'phoneNo': ExampleContactAdapter,
                    }
        for name in names:
            field = nr.getProperty(context, name)
            self.assert_(isinstance(field.context, adapters[field.getName()]))

    def test_widget(self):
        nr = component.getUtility(INamespaceManager, namespace)
        context = Content(None, 'contenttype')
        instream = StringIO('')
        request  = WebDAVRequest(instream, {})

        agewidget = nr.getWidget(context, request, 'age', 'a0')
        self.assert_(isinstance(agewidget, IntDAVWidget))

        namewidget = nr.getWidget(context, request, 'name', 'a0')
        xmlel = namewidget.renderProperty()
        self.assertEqual(xmlel.toxml(),
                         '<name xmlns="a0">The Other Michael Kerrin</name>')

    def test_has_property(self):
        nr = component.getUtility(INamespaceManager, namespace)
        context = Content(None, 'contenttype')

        self.assert_(nr.hasProperty(context, 'age'))
        self.assert_(nr.hasProperty(context, 'job') is False)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNamespaceRegistry))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest = 'test_suite')

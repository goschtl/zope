##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Test the gts ZCML namespace directives.

$Id: test_directives.py,v 1.1 2003/04/16 13:45:44 srichter Exp $
"""
import os
import unittest

from cStringIO import StringIO

from zope.component import getService
from zope.component.tests.placelesssetup import PlacelessSetup
from zope.configuration.xmlconfig import xmlconfig, Context, XMLConfig
from zope.configuration.exceptions import ConfigurationError

from zope.app.component.metaconfigure import managerHandler, provideInterface
import zope.app.mail
import zope.app.interfaces.mail 

template = """<zopeConfigure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:mail='http://namespaces.zope.org/mail'>
   xmlns:test='http://www.zope.org/NS/Zope3/test'>
   %s
   </zopeConfigure>"""


class DirectivesTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        managerHandler('defineService', 'Mail',
                       zope.app.interfaces.mail.IMailService)
        provideInterface('zope.app.interfaces.mail.IMailService',
                         zope.app.interfaces.mail.IMailService)
        XMLConfig('metameta.zcml', zope.configuration)()
        XMLConfig('meta.zcml', zope.app.mail)()

    def test_mailservice(self):        
        xmlconfig(StringIO(template % (
            '''            
            <mail:mailservice name="Mail"
               hostname="somehost" port="125"
               username="foo" password="bar"
               class=".mail.AsyncMailService" 
               permission="zope.Public" />
            '''
            )), None, Context([], zope.app.mail))
        service = getService(None, 'Mail') 
        self.assertEqual('AsyncMailService', service.__class__.__name__)
        self.assertEqual('somehost', service.hostname)
        self.assertEqual(125, service.port)
        self.assertEqual('foo', service.username)
        self.assertEqual('bar', service.password)

    def test_mailer(self):
        xmlconfig(StringIO(template % (
            '''            
            <mail:mailservice class=".mail.AsyncMailService" 
                permission="zope.Public" />

            <mail:mailer name="TestSimpleMailer" class=".mailer.SimpleMailer" 
                serviceType="Mail" default="True" /> 
            '''
            )), None, Context([], zope.app.mail))

        service = getService(None, "Mail")
        self.assertEqual("TestSimpleMailer", service.getDefaultMailerName())
        self.assertEqual(service._AsyncMailService__mailers['TestSimpleMailer'],
                         service.createMailer('TestSimpleMailer').__class__)


def test_suite():
    return unittest.makeSuite(DirectivesTest)

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())

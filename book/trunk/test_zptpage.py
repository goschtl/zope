##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Code for the Zope 3 Book's Functional Tests Chapter

$Id: test_templatedpage.py,v 1.1.1.1 2004/02/18 18:07:08 srichter Exp $
"""



import time
import unittest

from transaction import get_transaction
from zope.app.tests.functional import BrowserTestCase
from zope.app.zptpage.zptpage import ZPTPage

class TemplatedPageTests(BrowserTestCase):
    """Funcional tests for Templated Page."""

    template = u'''\
    <html>
      <body>
        <h1 tal:content="modules/time/asctime" />
      </body>
    </html>'''

    template2 = u'''\
    <html>
      <body>
        <h1 tal:content="modules/time/asctime">time</h1>
      </body>
    </html>'''

    def createPage(self):
        root = self.getRootFolder()
        root['zptpage'] = ZPTPage()
        root['zptpage'].setSource(self.template, 'text/html')
        get_transaction().commit()

    def test_add(self):
        response = self.publish(
            "/+/zope.app.zptpage.ZPTPage=",
            basic='mgr:mgrpw', 
            form={'add_input_name' : u'newzptpage',
                  'field.expand.used' : u'',
                  'field.source' : self.template,
                  'field.evaluateInlineCode.used' : u'',
                  'field.evaluateInlineCode' : u'on',
                  'UPDATE_SUBMIT' : 'Add'})

        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(response.getHeader('Location'),
                         'http://localhost/@@contents.html')
        
        zpt = self.getRootFolder()['newzptpage']
        self.assertEqual(zpt.getSource(), self.template)
        self.assertEqual(zpt.evaluateInlineCode, True)

    def test_editCode(self):
        self.createPage()
        response = self.publish(
            "/zptpage/@@edit.html",
            basic='mgr:mgrpw', 
            form={'field.expand.used' : u'',
                  'field.source' : self.template2,
                  'UPDATE_SUBMIT' : 'Change'})
        self.assertEqual(response.getStatus(), 200)
        self.assert_('&gt;time&lt;' in response.getBody())
        zpt = self.getRootFolder()['zptpage']
        self.assertEqual(zpt.getSource(), self.template2)
        self.checkForBrokenLinks(response.getBody(), response.getPath(),
                                 'mgr:mgrpw')

    def test_index(self):
        self.createPage()
        t = time.asctime()
        response = self.publish("/zptpage", basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        self.assert_(response.getBody().find('<h1>'+t+'</h1>') != -1)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TemplatedPageTests),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')

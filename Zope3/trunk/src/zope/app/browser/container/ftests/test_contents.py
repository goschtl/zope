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
"""

$Id: test_contents.py,v 1.3 2003/06/21 21:21:59 jim Exp $
"""

import unittest

from zope.testing.functional import BrowserTestCase
from zope.app.content.file import File
from transaction import get_transaction
from zope.app import zapi
from zope.app.interfaces.dublincore import IZopeDublinCore

class Test(BrowserTestCase):

    def test_inplace_add(self):
        root = self.getRootFolder()
        self.assert_('foo' not in root)
        response = self.publish('/@@contents.html',
                                basic='mgr:mgrpw',
                                form={'type_name': u'File'})
        body = ' '.join(response.getBody().split())
        self.assert_(body.find('type="hidden" name="type_name"') >= 0)
        self.assert_(body.find('input name="new_value"') >= 0)
        self.assert_(body.find('type="submit" name="container_cancel_button"')
                     >= 0)
        self.assert_(body.find('type="submit" name="container_rename_button"')
                     < 0)

        response = self.publish('/@@contents.html',
                                basic='mgr:mgrpw',
                                form={'type_name': u'File',
                                      'new_value': 'foo'})
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(response.getHeader('Location'),
                         'http://localhost/@@contents.html')

        root._p_jar.sync()
        self.assert_('foo' in root)

    def test_inplace_rename_multiple(self):
        root = self.getRootFolder()
        root.setObject('foo', File())
        self.assert_('foo' in root)
        get_transaction().commit()

        # Check that we don't change mode if there are no items selected
        
        response = self.publish('/@@contents.html',
                                basic='mgr:mgrpw',
                                form={'container_rename_button': u''})
        body = ' '.join(response.getBody().split())
        self.assert_(body.find('input name="new_value:list"') < 0)
        self.assert_(body.find('type="submit" name="container_cancel_button"')
                     < 0)
        self.assert_(body.find('type="submit" name="container_rename_button"')
                     >= 0)
        self.assert_(body.find('div class="page_error"')
                     >= 0)


        # Check normal multiple select

        
        response = self.publish('/@@contents.html',
                                basic='mgr:mgrpw',
                                form={'container_rename_button': u'',
                                      'ids': ['foo']})
        body = ' '.join(response.getBody().split())
        self.assert_(body.find('input name="new_value:list"') >= 0)
        self.assert_(body.find('type="submit" name="container_cancel_button"')
                     >= 0)
        self.assert_(body.find('type="submit" name="container_rename_button"')
                     < 0)

        response = self.publish('/@@contents.html',
                                basic='mgr:mgrpw',
                                form={'rename_ids': ['foo'],
                                      'new_value': ['bar']})
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(response.getHeader('Location'),
                         'http://localhost/@@contents.html')

        root._p_jar.sync()
        self.assert_('foo' not in root)
        self.assert_('bar' in root)


    def test_inplace_rename_single(self):
        root = self.getRootFolder()
        root.setObject('foo', File())
        self.assert_('foo' in root)
        get_transaction().commit()
        
        response = self.publish('/@@contents.html',
                                basic='mgr:mgrpw',
                                form={'rename_ids': ['foo']})
        body = ' '.join(response.getBody().split())
        self.assert_(body.find('input name="new_value:list"') >= 0)
        self.assert_(body.find('type="submit" name="container_cancel_button"')
                     >= 0)
        self.assert_(body.find('type="submit" name="container_rename_button"')
                     < 0)

        response = self.publish('/@@contents.html',
                                basic='mgr:mgrpw',
                                form={'rename_ids': ['foo'],
                                      'new_value': ['bar']})
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(response.getHeader('Location'),
                         'http://localhost/@@contents.html')

        root._p_jar.sync()
        self.assert_('foo' not in root)
        self.assert_('bar' in root)

    def test_inplace_change_title(self):
        root = self.getRootFolder()
        root.setObject('foo', File())
        get_transaction().commit()
        self.assert_('foo' in root)
        dc = zapi.getAdapter(root['foo'], IZopeDublinCore)
        self.assert_(dc.title == '')

        response = self.publish('/@@contents.html',
                                basic='mgr:mgrpw',
                                form={'retitle_id': u'foo'})
        body = ' '.join(response.getBody().split())
        self.assert_(body.find('type="hidden" name="retitle_id"') >= 0)
        self.assert_(body.find('input name="new_value"') >= 0)
        self.assert_(body.find('type="submit" name="container_cancel_button"')
                     >= 0)
        self.assert_(body.find('type="submit" name="container_rename_button"')
                     < 0)

        response = self.publish('/@@contents.html',
                                basic='mgr:mgrpw',
                                form={'retitle_id': u'foo',
                                      'new_value': u'test title'})
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(response.getHeader('Location'),
                         'http://localhost/@@contents.html')

        root._p_jar.sync()
        self.assert_('foo' in root)
        dc = zapi.getAdapter(root['foo'], IZopeDublinCore)
        self.assert_(dc.title == 'test title')



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    return suite

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')

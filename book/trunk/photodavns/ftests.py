##############################################################################
#
# Copyright (c) 2003, 2004 Zope Corporation and Contributors.
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
"""IPhoto Namespace functional tests

$Id: ftests.py,v 1.1.1.1 2004/02/18 18:07:08 srichter Exp $
"""
import unittest
from transaction import get_transaction
from xml.dom.minidom import parseString as parseXML
from zope.app.file.image import Image
from zope.app.dav.ftests.dav import DAVTestCase
from book.photodavns.interfaces import IPhoto
from book.photodavns import ImagePhotoNamespace

property_request = '''\
<?xml version="1.0" encoding="utf-8" ?>
<propfind xmlns="DAV:">
  <prop xmlns:photo="http://namespaces.zope.org/dav/photo/1.0">
    <photo:height />
    <photo:width />
    <photo:equivalent35mm />
    <photo:aperture />
    <photo:exposureTime />
  </prop>
</propfind>
'''
   
data = {'height': 768, 'width': 1024, 'equivalent35mm': u'41 mm',
        'aperture': u'f/2.8', 'exposureTime': 0.031}

class IPhotoNamespaceTests(DAVTestCase):

    def createImage(self):
        img = Image()
        photo = ImagePhotoNamespace(img)
        for name, value in data.items():
            setattr(photo, name, value)
        root = self.getRootFolder()
        root['img.jpg'] = img
        get_transaction().commit()
        
    def test_propfind_fields(self):
        self.createImage()
        response = self.publish(
            '/img.jpg/',
            env={'REQUEST_METHOD':'PROPFIND',
                 'HTTP_Content_Type': 'text/xml'},
            request_body=property_request)
        self.assertEqual(response.getStatus(), 207)
        xml = parseXML(response.getBody())
        node = xml.documentElement.getElementsByTagName('prop')[0]

        for name, value in data.items():
            attr_node = node.getElementsByTagName(name)[0]
            self.assertEqual(attr_node.firstChild.data, unicode(value))
            
def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(IPhotoNamespaceTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

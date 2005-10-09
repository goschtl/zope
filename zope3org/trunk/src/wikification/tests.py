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

$Id: tests.py 38895 2005-10-07 15:09:36Z dominikhuber $
"""
__docformat__ = 'restructuredtext'

import unittest

import zope.component
import zope.interface
import zope.app.testing.setup

from zope.testing import doctest, doctestunit
from zope.app import zapi
from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.annotation.interfaces import IAnnotations
from zope.app.annotation.interfaces import IAnnotatable
from zope.app.annotation.attribute import AttributeAnnotations
from zope.app.container.interfaces import IContained
from zope.app.traversing.interfaces import ITraversable, ITraverser
from zope.app.traversing.interfaces import IPhysicallyLocatable
from zope.app.traversing.interfaces import IContainmentRoot
from zope.app.traversing.adapters import DefaultTraversable
from zope.app.location.traversing import LocationPhysicallyLocatable
from zope.app.traversing.adapters import RootPhysicallyLocatable
from zope.app.traversing.adapters import Traverser

from zope.app.dublincore.interfaces import IZopeDublinCore
from zope.app.dublincore.annotatableadapter import ZDCAnnotatableAdapter

from zope.app.folder import rootFolder
from zope.app.folder import Folder
from zope.app.file import File




example1 = u"""<html>
    <body>
        <p>Wikifiable</p>
        <p>An <a href="target">existing link</a></p>
        <p>A <a href="newitem">new page</a></p>
        <p>A <a href="folder1/newitem">new page in a subfolder</a></p>
        <p>A [New Subject]</p>
        <p>An <a href="http://www.google.org">external absolute link</a></p>
        <p>An <a href="http://127.0.0.1/site/target">internal absolute link</a></p>
    </body>
</html>"""



def buildSampleSite() :
    """ Build a sample structure
    
        root
            index.html          (with example1 as content)
            target              (an existing file)
            folder              (a sample folder)
            
        Usage :
        
        
        >>> site = buildSampleSite()
        >>> IZopeDublinCore(site).title
        u'Wiki site'

        
        
    """
    root = rootFolder()
    IZopeDublinCore(root).title = u'Wiki site'
    root.__name__ = u"site"
    root[u"target"] = File()
    folder = root[u"folder"] = Folder()
    index = root[u"index.html"] = File(example1, 'text/html')
    
    IZopeDublinCore(index).title = u'Wiki page'
    return root    



def setUpWikification(test) :
   
    zope.app.testing.setup.placefulSetUp()
    
    from zope.app.testing import ztapi
    
    zope.interface.classImplements(File, IAnnotatable)
    zope.interface.classImplements(Folder, IAnnotatable)
    zope.interface.classImplements(File, IAttributeAnnotatable)
    zope.interface.classImplements(Folder, IAttributeAnnotatable)
    
    zope.component.provideAdapter(Traverser, [None], ITraverser)
    zope.component.provideAdapter(DefaultTraversable, [None], ITraversable)
    zope.component.provideAdapter(LocationPhysicallyLocatable,
                                            [None], IPhysicallyLocatable)
    zope.component.provideAdapter(RootPhysicallyLocatable,
                                            [IContainmentRoot], 
                                            IPhysicallyLocatable)

    zope.component.provideAdapter(ZDCAnnotatableAdapter,
                                            [IAnnotatable], 
                                            IZopeDublinCore)
 
    
def tearDownWikification(test) :
    zope.app.testing.setup.placefulTearDown()   



def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(setUp=setUpWikification, 
                                    tearDown=tearDownWikification),
                                    
        doctest.DocFileSuite("README.txt", 
                    setUp=setUpWikification, 
                    tearDown=tearDownWikification,
                    globs={'zapi': zope.app.zapi,
                           'pprint': doctestunit.pprint,
                           'TestRequest': zope.publisher.browser.TestRequest                                
                          },
                    optionflags=doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

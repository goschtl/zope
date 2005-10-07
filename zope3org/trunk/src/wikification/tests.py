import unittest

import zope
from zope.testing import doctest, doctestunit
from zope.app.testing import ztapi
from zope.app.testing.setup import placefulSetUp, placefulTearDown

from zope.interface import classImplements
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
    """
    root = rootFolder()
    root.__name__ = u"site"
    root[u"target"] = File()
    folder = root[u"folder"] = Folder()
    root[u"index.html"] = File(example1, 'text/html')    
    return root    



def setUpWikification(test) :
   
    placefulSetUp()
    
    classImplements(File, IAnnotatable)
    classImplements(Folder, IAnnotatable)
    classImplements(File, IAttributeAnnotatable)
    classImplements(Folder, IAttributeAnnotatable)
    
    ztapi.provideAdapter(None, ITraverser, Traverser)
    ztapi.provideAdapter(None, ITraversable, DefaultTraversable)
    ztapi.provideAdapter(None, IPhysicallyLocatable,
                                LocationPhysicallyLocatable)
    ztapi.provideAdapter(IContainmentRoot, IPhysicallyLocatable, 
                                RootPhysicallyLocatable)

    
def tearDownWikification(test) :
    placefulTearDown()   



def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite("README.txt", 
                                setUp=setUpWikification, 
                                tearDown=tearDownWikification,
                                globs={'zapi': zope.app.zapi,
                                       'pprint': doctestunit.pprint,
                                       'TestRequest': zope.publisher.browser.TestRequest                                
                                        },
                                optionflags=doctest.NORMALIZE_WHITESPACE+
                                            doctest.ELLIPSIS
                             ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

import doctest, unittest

from zope.app.testing import ztapi
from zope.component.tests.placelesssetup import PlacelessSetup

from zope.interface import classImplements
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

from zope.app.folder import Folder
from zope.app.file import File


example1 = u"""<html>
<body>
<p>Wikifiable</p>
<p>An <a href="folder1/target">existing link</a></p>
<p>A <a href="folder1/newitem">new page</a></p>
<p>A [New Subject]</a></p>
</body>
</html>"""

ps = PlacelessSetup() 

def buildSampleSite() :
    
    site = Folder()
    
    folder1 = site[u"folder1"] = Folder()
    folder2 = site[u"folder2"] = Folder()

    site[u"index.html"] = File(example1, 'text/html')
    folder1[u"target"] = File()
    return site    


def renderWikiPage(file) :
    return file.data

def setUpWikification(test) :
    
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
    ps.tearDown()   



def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite("README.txt", setUp=setUpWikification, 
                                           tearDown=tearDownWikification),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

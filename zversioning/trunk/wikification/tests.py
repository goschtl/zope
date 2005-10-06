import doctest, unittest


from zope.app.folder import Folder
from zope.app.file import File


example1 = u"""<html><body><p>Wikifiable</p>
<p>An <a href="folder1/target">existing link</a></p>
<p>A <a href="folder1/newitem">new page</a></p>
</body></html>"""


def buildSampleSite() :
    
    site = Folder()
    
    folder1 = site[u"folder1"] = Folder()
    folder2 = site[u"folder2"] = Folder()

    site[u"index.html"] = File(example1, 'text/html')
    return site    


def setUpWikification(test) :
    pass    
    
def tearDownWikification(test) :
    pass    



def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite("README.txt", setUp=setUpWikification, 
                                           tearDown=tearDownWikification),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

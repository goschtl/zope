"""
Let's create a Mammoth object in the root folder so we can access
views through the publisher:

  >>> from zope.app.testing.functional import getRootFolder
  >>> root = getRootFolder()
  >>> root['app'] = App()

As an anonymous user, we only see the unprotected menu items:

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> browser.open('http://localhost/app/view')
  >>> browser.contents
  '...Hello World...'
  
  >>> browser.open('http://localhost/app/indexfs')
  >>> browser.contents
  '...Hello World...'

"""
import grok
import megrok.z3cpt

# You can either refer to the menu class itself:

class App(grok.Model):
    pass

class IndexFS(grok.View):
    pass

class Index(grok.View):
    grok.name('view')
    person=""

    def update(self):
	self.person="Christian"

index = megrok.z3cpt.z3cPageTemplate("""
                 <html xmlns="http://www.w3.org/1999/xhtml"
		       xmlns:tal="http://xml.zope.org/namespaces/tal">
                  <div>
                   Hello World!
                  </div>
		  <span tal:content="view.person" />
                 </html>
              """)


def test_suite():
    from zope.testing import doctest
    from megrok.z3cpt.tests import FunctionalLayer
    suite = doctest.DocTestSuite(optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
    suite.layer = FunctionalLayer
    return suite

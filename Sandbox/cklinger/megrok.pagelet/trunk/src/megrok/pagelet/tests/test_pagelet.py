"""
  >>> from zope.component import getUtility
  >>> from zope.publisher.browser import TestRequest
  >>> from z3c.template.interfaces import ILayoutTemplate
  >>> page = Page()
  >>> from zope.interface import Interface
  >>> from zope.component import getMultiAdapter
  >>> request = TestRequest()
  >>> view = getMultiAdapter((page, request), name="mypagelet")
  >>> print view()
  <html>
   <body>
     <div class="layout"><b> I am a MotherFucking  pagelet </b></div>
   </body>
  </html>

  >>> print view.render()
  <b> I am a MotherFucking  pagelet </b>

What happens if we don´t have a Layout for a pagelet

   >>> document = Document()
   >>> view = getMultiAdapter((document, request), name='documentpagelet')
   >>> view()
   Traceback (most recent call last):
   ...
   ComponentLookupError: ...

Now I want to see a Pagelet with a template in xxx_templates/xxx.pt

   >>> viewt = getMultiAdapter((page, request), name='pageletwithtemplate')
   >>> print viewt()
   <html>
    <body>
      <div class="layout"><p> I am a renderd template of a pagelet </p>
   </div>
    </body>
   </html>
   >>> print viewt.render()
   <p> I am a renderd template of a pagelet </p>
"""
import grok
import megrok.pagelet
from zope.interface import Interface
from zope.component import getMultiAdapter

class Page(grok.Context):
    pass

class MyPagelet(megrok.pagelet.Pagelet):
    grok.context(Page)

    def render(self):
        return "<b> I am a MotherFucking  pagelet </b>"

class PageletWithTemplate(megrok.pagelet.Pagelet):
    grok.context(Page)


class MyLayout(megrok.pagelet.Layout):
    grok.context(Page)
    megrok.pagelet.template('templates/playout.pt')


class Document(grok.Context):
    pass

class DocumentPagelet(megrok.pagelet.Pagelet):
    grok.context(Document)

    def render(self):
	return "<b> Render without a Pagelet"



def test_suite():
    from zope.testing import doctest
    from megrok.pagelet.tests import FunctionalLayer
    import interlude
    suite = doctest.DocTestSuite(optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite

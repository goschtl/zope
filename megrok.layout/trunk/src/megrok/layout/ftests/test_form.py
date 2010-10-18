"""
  >>> from megrok.layout import ILayout
  >>> from zope.component import getMultiAdapter
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> cow = Cow()
  >>> mylayout = getMultiAdapter((request, cow), ILayout)

  Display form:
  >>> myview = getMultiAdapter((cow, request), name='myview')
  >>> print myview()
  <html>
   <body>
     <div class="layout"><form ...
     ...<span>Color</span>...
     ...<div class="widget">globally dark</div>...
     ...</form>
     </div>
   </body>
  </html>

  >>> myview
  <megrok.layout.ftests.test_form.MyView object at ...>
  >>> myview.layout
  <megrok.layout.ftests.test_form.Master object at ...>
  >>> print myview.content()
  <form action="http://127.0.0.1" method="post"
        class="edit-form" enctype="multipart/form-data">
     ...<span>Color</span>...
     ...<div class="widget">globally dark</div>...
  </form>

  Edit form:
  >>> myeditview = getMultiAdapter((cow, request), name='myeditview')
  >>> print myeditview()
  <html>
   <body>
     <div class="layout"><form ...
     ...<span>Color</span>...
     ... value="globally dark" ...
     ... value="Apply" ...
     ...</form>
     </div>
   </body>
  </html>

  >>> myeditview
  <megrok.layout.ftests.test_form.MyEditView object at ...>
  >>> myeditview.layout
  <megrok.layout.ftests.test_form.Master object at ...>
  >>> print myeditview.content()
  <form action="http://127.0.0.1" method="post"
        class="edit-form" enctype="multipart/form-data">
     ...<span>Color</span>...
     ... value="globally dark" ...
     ... value="Apply" ...
  </form>


"""
import grokcore.component as grok
from grokcore.view import templatedir

from zope import interface, schema
from megrok.layout import Layout, DisplayForm, EditForm

templatedir('templates')


class ICowProperties(interface.Interface):

    color = schema.TextLine(title=u"Color")


class Cow(grok.Context):
    grok.implements(ICowProperties)

    color = u"globally dark"


class Master(Layout):
    grok.name('master')
    grok.context(Cow)


class MyView(DisplayForm):
    grok.context(Cow)


class MyEditView(EditForm):
    grok.context(Cow)


def test_suite():
    from zope.testing import doctest
    from megrok.layout.ftests import FunctionalLayer
    suite = doctest.DocTestSuite(
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
        )
    suite.layer = FunctionalLayer
    return suite

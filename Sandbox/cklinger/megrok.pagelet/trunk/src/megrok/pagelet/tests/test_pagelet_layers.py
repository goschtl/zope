"""
  >>> from zope.app.testing.functional import getRootFolder
  >>> getRootFolder()["manfred"] = Mammoth()

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> browser.open("http://localhost/++skin++Basic/manfred/@@myview")
  >>> print browser.contents
  <html>
   <body>
     <div class="layout"><b>Yeah</b></div> 
   </body>
  </html>


  >>> browser.open("http://localhost/++skin++myskin/manfred/@@mynewview")
  >>> print browser.contents
  <html>
   <body>
     <div class="layer_layout"><b> This is the view in the Layer </b></div> 
   </body>
  </html>
"""

import grok
import megrok.pagelet

from zope.app.basicskin import IBasicSkin

grok.layer(IBasicSkin)

class MySkinLayer(grok.IBrowserRequest):
    pass

class MySkin(MySkinLayer):
    grok.skin('myskin')

class Mammoth(grok.Model):
    pass

class MyView(megrok.pagelet.Pagelet):
    grok.context(Mammoth)

    def render(self):
	return "<b>Yeah</b>"

class MyLayout(megrok.pagelet.Layout):
    grok.context(Mammoth)
    megrok.pagelet.template('templates/playout.pt')


class MyNewView(megrok.pagelet.Pagelet):
    grok.context(Mammoth)
    grok.layer(MySkinLayer)

    def render(self):
        return "<b> This is the view in the Layer </b>"

class MyLayerLayout(megrok.pagelet.Layout):
    grok.context(Mammoth)
    grok.layer(MySkinLayer)
    megrok.pagelet.template('templates/layer_layout.pt')

def test_suite():
    from zope.testing import doctest
    from megrok.pagelet.tests import FunctionalLayer
    suite = doctest.DocTestSuite(optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite




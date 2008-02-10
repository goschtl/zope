"""
Test the claimed directives.

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')

  >>> skinURL = 'http://localhost/++skin++namedskin'

Try opening page.htm which is registered in ftesting.zcml for
z3c.layer.IMinimalBrowserLayer.

  >>> browser.open(skinURL + '/page.html')
  >>> print browser.contents
  <BLANKLINE>
  <html>
  <head>
    <title>testing</title>
  </head>
  <body>
  <BLANKLINE>
    test page
  <BLANKLINE>
  </body>
  </html>
  <BLANKLINE>
  <BLANKLINE>

"""
import grok
import mars.layer

class IMyLayer(mars.layer.IMinimalLayer):
    pass

class MySkin(grok.Skin):
    grok.name('namedskin')
    grok.layer(IMyLayer)


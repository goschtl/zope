"""

  >>> import grok.testing
  >>> grok.testing.grok(__name__)

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')

  >>> skinURL = 'http://localhost/++skin++myskin'

Try opening page.htm which is registered in ftesting.zcml for
z3c.layer.IPageletBrowserLayer.

  >>> browser.open(skinURL + '/page.html')
  >>> print browser.contents
  <!DOCTYPE...
  <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
  <title>TestingSkin</title>
  </head>
  <body>
    test page
  <BLANKLINE>
  </body>
  </html>
  <BLANKLINE>


"""

import grok
import mars.layer

class IMyLayer(mars.layer.IPageletLayer):
    pass

class MySkin(grok.Skin):
    grok.layer(IMyLayer)



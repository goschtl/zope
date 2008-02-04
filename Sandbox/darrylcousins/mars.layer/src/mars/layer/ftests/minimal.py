"""

  >>> from zope.testbrowser.testing import Browser

  >>> manager = Browser()
  >>> manager.addHeader('Authorization', 'Basic mgr:mgrpw')
  >>> skinURL = 'http://localhost/++skin++MinimalTesting'
  >>> manager.open(skinURL + '/page.html')
  >>> manager.url
  'http://localhost/++skin++MinimalTesting/page.html'

  >>> skinURL = 'http://localhost/++skin++minskin'

Try opening page.htm which is registered in ftesting.zcml for
z3c.layer.IMinimalBrowserLayer.

  >>> browser = Browser()
  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')

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

# layer can be set on module level and will therefore be the layer
# for all views, template and macros in the module
grok.layer(IMyLayer)

class MinSkin(grok.Skin):
    pass


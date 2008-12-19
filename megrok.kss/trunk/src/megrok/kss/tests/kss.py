"""
  >>> from zope.publisher.browser import TestRequest
  >>> from zope.component import getMultiAdapter
  >>> request = TestRequest()

We create a view on the model and call the KSS action on the view. The
KSS action calls `self.view.render()`.

  >>> mymodel = TestModel('model1')
  >>> view = getMultiAdapter((mymodel, request), name="testview")
  >>> kss = getMultiAdapter((view, request), name="getId")
  >>> print kss()
  <?xml version="1.0" ?>
  <kukit xmlns="http://www.kukit.org/commands/1.1">
  <commands>
  <command selector="#click-me" name="replaceHTML"
           selectorType="">
      <param name="html"><![CDATA[Something silly!]]></param>
      <param name="withKssSetup">True</param>
  </command>
  </commands>
  </kukit>
  <BLANKLINE>

The KSS action can be called by non-authenticated users. We put our
model into the ZODB to make it browsable::

  >>> from zope.app.testing.functional import getRootFolder
  >>> root = getRootFolder()
  >>> root['model'] = mymodel

Now we start the test-browser and try to access our action as
non-authenticated users::
  
  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.open('http://localhost/model/@@testview/@@getId')
  >>> print browser.contents
  <?xml version="1.0" ?>
  <kukit xmlns="http://www.kukit.org/commands/1.1">
  <commands>
  <command selector="#click-me" name="replaceHTML"
           selectorType="">
      <param name="html"><![CDATA[Something silly!]]></param>
      <param name="withKssSetup">True</param>
  </command>
  </commands>
  </kukit>

"""

import grok
from megrok.kss import KSS


class TestModel(grok.Model):

    def __init__(self, id):
        """docstring for __init__"""
        self.id = id


class TestView(grok.View):

    def render(self):
        return self.context.id


class TestKSS(KSS):

    grok.view(TestView)
    grok.require(grok.Public)

    def getId(self):
        """Docstring for getId"""
        core = self.getCommandSet('core')
        core.replaceHTML('#click-me', 'Something silly!')

"""
  >>> from zope.publisher.browser import TestRequest
  >>> from zope.component import getMultiAdapter
  >>> request = TestRequest()

First we create a model. After that we get and call the KSS action on
it.

  >>> mymodel = TestModel('model1')
  >>> kssaction = getMultiAdapter((mymodel, request), name="getId")
  >>> print kssaction()
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

Second we create a view on the model and call the KSS action on the view. The
KSS action calls `self.view.render()`.

  >>> view = getMultiAdapter((mymodel, request), name="testview")
  >>> kssaction = getMultiAdapter((view, request), name="getId")
  >>> print kssaction()
  <?xml version="1.0" ?>
  <kukit xmlns="http://www.kukit.org/commands/1.1">
  <commands>
  <command selector="#click-me" name="replaceHTML"
           selectorType="">
      <param name="html"><![CDATA[model1]]></param>
      <param name="withKssSetup">True</param>
  </command>
  </commands>
  </kukit>
  <BLANKLINE>
"""

import grok
from megrok.kss import KSSActions, KSSActionsForView


class TestModel(grok.Model):

    def __init__(self, id):
        """docstring for __init__"""
        self.id = id


class TestView(grok.View):

    def render(self):
        return self.context.id


class TestKSSActions(KSSActions):

    grok.context(TestModel)

    def getId(self):
        """Docstring for getId"""
        core = self.getCommandSet('core')
        core.replaceHTML('#click-me', 'Something silly!')


class TestKSSActionsForView(KSSActionsForView):

    grok.view(TestView)

    def getId(self):
        """Docstring for getId"""
        core = self.getCommandSet('core')
        core.replaceHTML('#click-me', self.view.render())

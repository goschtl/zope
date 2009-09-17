"""
Sample data setup
-----------------

Let's create a sample container which we can use as our iterable context:

  >>> from zope.app.testing.functional import getRootFolder
  >>> root = getRootFolder()
  >>> cont = Container()

and set a parent for the cont:

  >>> root['conti'] = cont

Now setup some items:

  >>> cont[u'first'] = Content('First', 1)
  >>> cont[u'second'] = Content('Second', 2)
  >>> cont[u'third'] = Content('Third', 3)

  >>> from zope.component import getMultiAdapter
  >>> from zope.publisher.browser import TestRequest
  >>> table_view = getMultiAdapter((cont, TestRequest()), name=u"formtable") 
  >>> print table_view
  >>> table_with_template = getMultiAdapter((cont, TestRequest()), name=u"contentstablewithtemplate")
  >>> print table_with_template
"""

import grokcore.component as grok
from megrok.z3ctable.ftests import Container, Content
from megrok.z3cform.tabular import FormTable
from megrok.z3cform.base import button 
from megrok.z3ctable import CheckBoxColumn, NameColumn

class FormTable(FormTable):
    grok.context(Container)

    status = None

    def render(self):
        return self.renderFormTable()

class Name(NameColumn):
    grok.name('checkBox')
    grok.adapts(None, None, FormTable)
    weight = 0

#

class ContentsTableWithTemplate(FormTable):
    grok.context(Container)

    status = None

class MyId(NameColumn):
    grok.name('myid')
    grok.adapts(None, None, ContentsTableWithTemplate)
    weight = 0


def test_suite():
    from zope.testing import doctest
    from megrok.z3cform.tabular.tests import FunctionalLayer
    suite = doctest.DocTestSuite(
          optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite


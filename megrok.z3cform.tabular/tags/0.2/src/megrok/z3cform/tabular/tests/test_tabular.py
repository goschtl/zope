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
  >>> table_view = getMultiAdapter((cont, TestRequest()), name=u"myformtable")
  >>> print table_view()
  <form action="http://127.0.0.1" method="post"
        enctype="multipart/form-data" class="edit-form"
        name="formTable" id="formTable">
    <div class="viewspace">
      <div>
      <div class="tabluarTable">
        <table class="contents">
    <thead>
      <tr>
        <th>Name</th>
      </tr>
    </thead>
    <tbody>
      <tr class="even">
        <td>first</td>
      </tr>
      <tr class="odd">
        <td>second</td>
      </tr>
      <tr class="even">
        <td>third</td>
      </tr>
    </tbody>
  </table>
      </div>
      <div class="tabluarForm">
      </div>
    </div>
    </div>
    <div>
      <div class="buttons">
  <input id="formTable-buttons-cancel"
         name="formTable.buttons.cancel"
         class="submit-widget button-field" value="Cancel"
         type="submit" />
      </div>
    </div>
  </form>

  >>> table_with_template = getMultiAdapter((cont, TestRequest()), name=u"contentstablewithtemplate")
  >>> print table_with_template()
  <html>
   <body>
    <form action="http://127.0.0.1" method="post"
        enctype="multipart/form-data" class="edit-form"
        name="formTable" id="formTable">
    <div class="viewspace">
      <div>
      <div class="tabluarTable">
        <table class="contents">
    <thead>
      <tr>
        <th>Name</th>
      </tr>
    </thead>
    <tbody>
      <tr class="even">
        <td>first</td>
      </tr>
      <tr class="odd">
        <td>second</td>
      </tr>
      <tr class="even">
        <td>third</td>
      </tr>
    </tbody>
  </table>
      </div>
      <div class="tabluarForm">
      </div>
    </div>
    </div>
    <div>
      <div class="buttons">
  <input id="formTable-buttons-cancel"
         name="formTable.buttons.cancel"
         class="submit-widget button-field" value="Cancel"
         type="submit" />
      </div>
    </div>
  </form>
   </body>
  </html>
"""

import grokcore.component as grok

from megrok.z3cform.base import button
from megrok.z3cform.tabular import FormTable
from megrok.z3ctable import CheckBoxColumn, NameColumn, table
from megrok.z3ctable.ftests import Container, Content


class MyFormTable(FormTable):
    grok.context(Container)
    status = None

    def render(self):
        return self.renderFormTable()


class Name(NameColumn):
    grok.name('checkBox')
    grok.context(Container)
    table(MyFormTable)
    weight = 0


class ContentsTableWithTemplate(FormTable):
    grok.context(Container)
    status = None


class MyId(NameColumn):
    grok.name('myid')
    grok.context(Container)
    table(ContentsTableWithTemplate)
    weight = 0


def test_suite():
    from zope.testing import doctest
    from megrok.z3cform.tabular.tests import FunctionalLayer
    suite = doctest.DocTestSuite(
          optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite

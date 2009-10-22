"""
Sample data setup
-----------------

Let's create a sample container which we can use as our iterable context:

  >>> from zope.app.testing.functional import getRootFolder
  >>> root = getRootFolder()
  >>> cont = Container()

and set a parent for the cont:

  >>> root['my_container1'] = cont

Now setup some items:

  >>> cont[u'first'] = Content('First', 1)
  >>> cont[u'second'] = Content('Second', 2)
  >>> cont[u'third'] = Content('Third', 3)

Call the Table with getMultiAdapter
-----------------------------------

  >>> from zope.component import getMultiAdapter
  >>> from zope.publisher.browser import TestRequest
  >>> table_in_layout = getMultiAdapter((cont, TestRequest()), name=u"tableinlayout")
  >>> print table_in_layout()
  <html><form action="http://127.0.0.1" method="post"
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
  </html>
  >>> delete_table_in_layout = getMultiAdapter((cont, TestRequest()), name=u"formtablepagewithtemplate")
  >>> print delete_table_in_layout()
  <html><div id="content">
    <form action="http://127.0.0.1" method="post"
        enctype="multipart/form-data" class="edit-form"
        name="deleteFormTable" id="deleteFormTable">
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
  <input id="deleteFormTable-buttons-delete"
         name="deleteFormTable.buttons.delete"
         class="submit-widget button-field" value="Delete"
         type="submit" />
      </div>
    </div>
  </form>
  </div>
  </html>
"""

import grokcore.component as grok

from megrok import layout
from megrok.z3cform.base import button
from megrok.z3cform.tabular import FormTablePage, DeleteFormTablePage
from megrok.z3ctable import CheckBoxColumn, NameColumn, table
from megrok.z3ctable.ftests import Container, Content
from zope.component import Interface


class Layout(layout.Layout):
    grok.context(Interface)

    def render(self):
        return "<html>%s</html>" %self.view.content()


class TableInLayout(FormTablePage):
    grok.context(Container)

    def render(self):
        return self.renderFormTable()


class Uid(NameColumn):
    grok.name('uid')
    table(FormTablePage)
    grok.context(Container)
    weight = 1


class FormTablePageWithTemplate(DeleteFormTablePage):
    grok.context(Container)


class Name(NameColumn):
    grok.name('Name')
    table(FormTablePageWithTemplate)
    grok.context(Container)
    weight = 1


def test_suite():
    from zope.testing import doctest
    from megrok.z3cform.tabular.tests import FunctionalLayer
    suite = doctest.DocTestSuite(
          optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite

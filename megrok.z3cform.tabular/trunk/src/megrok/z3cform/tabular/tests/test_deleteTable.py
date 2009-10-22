"""
Sample data setup
-----------------

Let's create a sample container which we can use as our iterable context:

  >>> from zope.app.testing.functional import getRootFolder
  >>> root = getRootFolder()
  >>> cont = Container()

and set a parent for the cont:

  >>> root['cont'] = cont

Now setup some items:

  >>> cont[u'first'] = Content('First', 1)
  >>> cont[u'second'] = Content('Second', 2)
  >>> cont[u'third'] = Content('Third', 3)

  >>> from zope.component import getMultiAdapter
  >>> from zope.publisher.browser import TestRequest
  >>> delete_view = getMultiAdapter((cont, TestRequest()), name=u"deletetable")
  >>> print delete_view()
  <form action="http://127.0.0.1" method="post"
        enctype="multipart/form-data" class="edit-form"
        name="deleteFormTable" id="deleteFormTable">
    <div class="viewspace">
      <div>
      <div class="tabluarTable">
        <table class="contents">
    <thead>
      <tr>
        <th>X</th>
        <th>Name</th>
      </tr>
    </thead>
    <tbody>
      <tr class="even">
        <td><input type="checkbox" class="checkbox-widget" name="deleteFormTable-checkBox-0-selectedItems-first" value="first"  /></td>
        <td>first</td>
      </tr>
      <tr class="odd">
        <td><input type="checkbox" class="checkbox-widget" name="deleteFormTable-checkBox-0-selectedItems-second" value="second"  /></td>
        <td>second</td>
      </tr>
      <tr class="even">
        <td><input type="checkbox" class="checkbox-widget" name="deleteFormTable-checkBox-0-selectedItems-third" value="third"  /></td>
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


Now call the table with the testbrowser
---------------------------------------

   >>> from zope.testbrowser.testing import Browser
   >>> browser = Browser()

   >>> browser.handleErrors = False
   >>> #browser.addHeader('Authorization', 'Basic user:user')
   >>> browser.open('http://localhost/cont/deletetable')
   >>> form = browser.getForm()
   >>> form.getControl(name='deleteFormTable-checkBox-0-selectedItems-first').value = "first"
   >>> form.submit('Delete')

   >>> print browser.contents
   <form...
       <div class="status">
            <div class="summary">Data successfully deleted</div>
       </div>
   ...
        <table class="contents">
    <thead>
      <tr>
        <th>X</th>
        <th>Name</th>
      </tr>
    </thead>
    <tbody>
      <tr class="even">
        <td><input type="checkbox" class="checkbox-widget" name="deleteFormTable-checkBox-0-selectedItems-second" value="second"  /></td>
        <td>second</td>
      </tr>
      <tr class="odd">
        <td><input type="checkbox" class="checkbox-widget" name="deleteFormTable-checkBox-0-selectedItems-third" value="third"  /></td>
        <td>third</td>
      </tr>
    </tbody>
   </table>
   ...


"""

import grokcore.component as grok

from megrok.z3cform.base import button
from megrok.z3cform.tabular import DeleteFormTable
from megrok.z3ctable import CheckBoxColumn, NameColumn
from megrok.z3ctable.ftests import Container, Content


class DeleteTable(DeleteFormTable):
    grok.context(Container)

    status = None

    def executeDelete(self, item):
        del self.context[item.__name__]

    def render(self):
        return self.renderFormTable()


class CheckBox(CheckBoxColumn):
    grok.name('checkBox')
    grok.context(Container)
    weight = 0

    def getItemKey(self, item):
        return '%s-selectedItems-%s' % (self.id, item.__name__)


class Name(NameColumn):
    grok.name('MyName')
    grok.context(Container)
    weight = 99


def test_suite():
    from zope.testing import doctest
    from megrok.z3cform.tabular.tests import FunctionalLayer
    suite = doctest.DocTestSuite(
          optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite

======================
megrok.z3cform.tabular
======================

With the help of this package you can create tables inside forms.
Think on a folder listing where you have a checkbox on the first
column and you can check the rows you want to modify. 
Such modifcations are for example:

 - edit 
 - delete 
 - change workflow state

megrok.z3cform.tabular is based on these existing megrok packages:

 - megrok.layout
 - megrok.z3ctable
 - megrok.z3cform.base
 - megrok.z3cform.ui


Example
-------

First we have to setup a container with some objects.

   >>> from zope.app.testing.functional import getRootFolder
   >>> root = getRootFolder()

   >>> from zope.app.container import btree
   >>> class Container(btree.BTreeContainer):
   ...     """Sample container."""
   ...     __name__ = u'container'
   >>> container = Container()


   >>> root['container'] = container


   >>> class Content(object):
   ...     """Sample content."""
   ...     def __init__(self, title, number):
   ...         self.title = title
   ...         self.number = number
       

   >>> container[u'first'] = Content('First', 1)
   >>> container[u'second'] = Content('Second', 2)
   >>> container[u'third'] = Content('Third', 3)

   >>> len(container)
   3

Ok now we have a container with three objects in it. Now we
can create a tabular view for this container:

   >>> from megrok.z3cform.tabular import FormTable
   >>> import grokcore.component as grok
   >>> from megrok.z3cform.base import button, extends

   >>> class FormTableView(FormTable):
   ...     grok.context(Container)
   ...     extends(FormTable)
   ...
   ...     @button.buttonAndHandler(u'ChangeWorkflowState')
   ...     def handleChangeWorkflowState(self, action):
   ...         print 'success'
   ...
   ...     def render(self):
   ...         return self.renderFormTable()


   >>> grok.testing.grok_component('formtableview', FormTableView)
   True

   >>> from megrok.z3ctable import table, CheckBoxColumn, NameColumn
   >>> class CheckBox(CheckBoxColumn):
   ...     grok.name('checkBox')
   ...     grok.context(Container)
   ...     table(FormTableView)

   >>> grok.testing.grok_component('checkbox', CheckBox)
   True

   >>> class Name(NameColumn):
   ...     grok.name('name')
   ...     grok.context(Container)
   ...     table(FormTableView)

   >>> grok.testing.grok_component('name', Name)
   True

Ok now we can call the FormTableView on the container. We
should see a table with three rows and two columns.
There is a default Cancel button and our custom
ChangeWorkflowState button.

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()

  >>> from zope.component import getMultiAdapter
  >>> formtableview = getMultiAdapter((container, request), name="formtableview")
  >>> formtableview
  <FormTableView 'formtableview'>

  >>> formtableview.update()
  >>> print formtableview() 
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
        <th>X</th>
      </tr>
    </thead>
    <tbody>
      <tr class="even">
        <td>first</td>
        <td><input type="checkbox" class="checkbox-widget" name="formTable-checkBox-1-selectedItems" value="first"  /></td>
      </tr>
      <tr class="odd">
        <td>second</td>
        <td><input type="checkbox" class="checkbox-widget" name="formTable-checkBox-1-selectedItems" value="second"  /></td>
      </tr>
      <tr class="even">
        <td>third</td>
        <td><input type="checkbox" class="checkbox-widget" name="formTable-checkBox-1-selectedItems" value="third"  /></td>
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
  <input id="formTable-buttons-changeworkflowstate"
         name="formTable.buttons.changeworkflowstate"
         class="submit-widget button-field"
         value="ChangeWorkflowState" type="submit" />
      </div>
    </div>
  </form>

This package works nicely with megrok.layout. There are some additional
BaseClasses available. Please take a look on the tests.

Enjoy...

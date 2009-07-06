"""
megrok.z3cform render
=====================

basic-setup
-----------

  >>> manfred = Mammoth()
  >>> from zope import component
  >>> from zope.interface import alsoProvides
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> alsoProvides(request, RenderSkin)

add forms
---------

  >>> add = component.getMultiAdapter((manfred, request), name='add')
  >>> print add()
  <form action="http://127.0.0.1" method="post"
          enctype="multipart/form-data" class="edit-form"
          name="form" id="form">
      <div class="viewspace">
          <div class="required-info">
             <span class="required">*</span>
             &ndash; required
          </div>
        <div>
              <div id="form-widgets-name-row" class="row">
                  <div class="label">
                    <label for="form-widgets-name">
                      <span>Name</span>
                      <span class="required">*</span>
                    </label>
                  </div>
                  <div class="widget">
        <input id="form-widgets-name" name="form.widgets.name"
               class="text-widget required textline-field"
               value="" type="text" />
    </div>
              </div>
              <div id="form-widgets-age-row" class="row">
                  <div class="label">
                    <label for="form-widgets-age">
                      <span>Age</span>
                      <span class="required">*</span>
                    </label>
                  </div>
                  <div class="widget">
        <input id="form-widgets-age" name="form.widgets.age"
               class="text-widget required int-field" value=""
               type="text" />
    </div>
              </div>
        </div>
      </div>
      <div>
        <div class="buttons">
    <input id="form-buttons-add" name="form.buttons.add"
           class="submit-widget button-field" value="Add"
           type="submit" />
        </div>
      </div>
    </form>


edit-forms
----------

  >>> edit = component.getMultiAdapter((manfred, request), name='edit')
  >>> print edit() 
  <form action="http://127.0.0.1" method="post"
          enctype="multipart/form-data" class="edit-form"
          name="form" id="form">
      <div class="viewspace">
          <div class="required-info">
             <span class="required">*</span>
             &ndash; required
          </div>
        <div>
              <div id="form-widgets-name-row" class="row">
                  <div class="label">
                    <label for="form-widgets-name">
                      <span>Name</span>
                      <span class="required">*</span>
                    </label>
                  </div>
                  <div class="widget">
        <input id="form-widgets-name" name="form.widgets.name"
               class="text-widget required textline-field"
               value="" type="text" />
    </div>
              </div>
              <div id="form-widgets-age-row" class="row">
                  <div class="label">
                    <label for="form-widgets-age">
                      <span>Age</span>
                      <span class="required">*</span>
                    </label>
                  </div>
                  <div class="widget">
        <input id="form-widgets-age" name="form.widgets.age"
               class="text-widget required int-field" value=""
               type="text" />
    </div>
              </div>
        </div>
      </div>
      <div>
        <div class="buttons">
    <input id="form-buttons-apply" name="form.buttons.apply"
           class="submit-widget button-field" value="Apply"
           type="submit" />
        </div>
      </div>
    </form>


display-forms
-------------

  >>> index = component.getMultiAdapter((manfred, request), name='index')
  >>> print index()
  <div class="viewspace">
        <div>
              <div id="form-widgets-name-row" class="row">
                  <div class="label">
                    <label for="form-widgets-name">
                      <span>Name</span>
                    </label>
                  </div>
                  <div class="widget">
        <span id="form-widgets-name"
              class="text-widget required textline-field"></span>
    </div>
              </div>
              <div id="form-widgets-age-row" class="row">
                  <div class="label">
                    <label for="form-widgets-age">
                      <span>Age</span>
                    </label>
                  </div>
                  <div class="widget">
        <span id="form-widgets-age"
              class="text-widget required int-field"></span>
    </div>
              </div>
        </div>
      </div>

"""
import grok

from zope import interface, schema
from zope.schema.fieldproperty import FieldProperty
from megrok import z3cform
from z3c.form import field

class RenderSkin(z3cform.FormLayer):
    grok.skin('renderskin')

grok.layer(RenderSkin)



class IMammoth(interface.Interface):

    name = schema.TextLine(title=u"Name")
    age = schema.Int(title=u"Age")

class Mammoth(grok.Model):
    
    interface.implements(IMammoth)

    name = FieldProperty(IMammoth['name'])
    age = FieldProperty(IMammoth['age'])

class Add(z3cform.AddForm):
    pass

class Edit(z3cform.EditForm):
    pass

class Index(z3cform.DisplayForm):
    pass

def test_suite():
    from zope.testing import doctest
    from megrok.z3cform.tests import FunctionalLayer
    suite = doctest.DocTestSuite(optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite


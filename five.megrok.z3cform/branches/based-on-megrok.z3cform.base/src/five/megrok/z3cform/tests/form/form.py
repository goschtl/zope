"""

  >>> grok.testing.grok(__name__)
  >>> from zope.publisher.browser import TestRequest
  >>> from zope.interface import alsoProvides
  >>> from zope.annotation.interfaces import IAttributeAnnotatable
  >>> from z3c.form.interfaces import IFormLayer
  >>> def make_request(form={}):
  ...     request = TestRequest()
  ...     request.form.update(form)
  ...     alsoProvides(request, IFormLayer)
  ...     alsoProvides(request, IAttributeAnnotatable)
  ...     return request

  >>> request = make_request()
  >>> from zope.component import getMultiAdapter
  >>> manfred = Mammoth('manfred')
  >>> edit = getMultiAdapter((manfred, request), name='edit')
  >>> print edit()
  <form action="http://127.0.0.1" method="post"
           enctype="multipart/form-data">
                  <div class="row">
                      <div class="field">
                        <label for="form-widgets-name">
                          <span>Name</span>
                        </label>
                        <span class="fieldRequired"
                              title="Required">
                          (Required)
                        </span>
                        <div class="widget">
        <input id="form-widgets-name" name="form.widgets.name"
               class="text-widget required textline-field"
               value="" type="text" />
                        </div>
                      </div>
                  </div>
                  <div class="row">
                      <div class="field">
                        <label for="form-widgets-age">
                          <span>Age</span>
                        </label>
                        <span class="fieldRequired"
                              title="Required">
                          (Required)
                        </span>
                        <div class="widget">
        <input id="form-widgets-age" name="form.widgets.age"
               class="text-widget required int-field" value=""
               type="text" />
                        </div>
                      </div>
                  </div>
                <div class="action">
    <input id="form-buttons-apply" name="form.buttons.apply"
           class="submit-widget button-field" value="Apply"
           type="submit" />
                </div>
  </form>
"""

from five import grok
from five.megrok import z3cform
from zope import interface, schema
from z3c.form import field
from zope.schema.fieldproperty import FieldProperty


class IMammoth(interface.Interface):
    name = schema.TextLine(title=u"Name")
    age = schema.Int(title=u"Age")


class Mammoth(grok.Model):
    grok.implements(IMammoth)

    name = FieldProperty(IMammoth['name'])
    age = FieldProperty(IMammoth['age'])


class Edit(z3cform.EditForm):
    fields = field.Fields(IMammoth)
    grok.context(IMammoth)

"""
A grok.EditForm uses applyData in update mode to save the form data on
the object.  Update mode means that only those fields are changed on
the object that need to be changed.

This is essentially the same narrative as 'editform_applydata'. Here
we test the whole procedure on fields from schemas:

  >>> import grok
  >>> from grok.ftests.form.editform_applydata_schema import Mammoth
  >>> grok.grok('grok.ftests.form.editform_applydata_schema')
  >>> getRootFolder()["manfred"] = Mammoth('Manfred the Mammoth', 'Really big')

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False

If we don't change any of the fields, there will no object modified
event and applyData will report no changes:

  >>> browser.open("http://localhost/manfred/@@edit")
  >>> browser.getControl("Apply").click()
  >>> 'No changes' in browser.contents
  True

If we change one field, only that attribute will be changed.  The
object modified event also reflects that:

  >>> browser.getControl(name="form.name").value = "Manfred the Big Mammoth"
  >>> browser.getControl("Apply").click()
  The 'name' property is being set.
  An IObjectModifiedEvent was sent for a mammoth with the following changes:
  IMammoth: name
  >>> 'Updated' in browser.contents
  True

Let's change the other field:

  >>> browser.getControl(name="form.size").value = "Enormously big"
  >>> browser.getControl("Apply").click()
  The 'size' property is being set.
  An IObjectModifiedEvent was sent for a mammoth with the following changes:
  IMammoth: size
  >>> 'Updated' in browser.contents
  True

And finally let's change both fields:

  >>> browser.getControl(name="form.name").value = "Manfred the Mammoth"
  >>> browser.getControl(name="form.size").value = "Really big"
  >>> browser.getControl("Apply").click()
  The 'name' property is being set.
  The 'size' property is being set.
  An IObjectModifiedEvent was sent for a mammoth with the following changes:
  IMammoth: name, size
  >>> 'Updated' in browser.contents
  True

"""
import grok
from zope import schema, interface

class IMammoth(interface.Interface):
    name = schema.TextLine(title=u"Name")
    size = schema.TextLine(title=u"Size")

class Mammoth(grok.Model):
    grok.implements(IMammoth)

    def __init__(self, name='', size=''):
        self._name = name
        self._size = size

    def getName(self):
        return self._name
    def setName(self, value):
        print "The 'name' property is being set."
        self._name = value
    name = property(getName, setName)

    def getSize(self):
        return self._size
    def setSize(self, value):
        print "The 'size' property is being set."
        self._size = value
    size = property(getSize, setSize)

class Edit(grok.EditForm):
    form_fields = grok.AutoFields(IMammoth)

@grok.subscribe(Mammoth, grok.IObjectModifiedEvent)
def notify_change_event(mammoth, event):
    print ("An IObjectModifiedEvent was sent for a mammoth with the "
           "following changes:")
    for descr in event.descriptions:
        print descr.interface.__name__ + ": " + ", ".join(descr.attributes)

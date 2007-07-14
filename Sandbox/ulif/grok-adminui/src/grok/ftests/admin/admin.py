"""
  >>> import grok
  >>> grok.grok('grok.ftests.admin.admin')

We fetch the standard page

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
  >>> browser.handleErrors = False
  >>> browser.open("http://localhost/")
  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ...
  ...      <legend>Add application</legend>
  ...

  >>> browser.getControl('Name your new app:',index=13).value = 'my-mammoth-manager'

We are able to add a mammoth manager...

  >>> browser.getControl('Create',index=13).click()

  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ...
  ... <legend>Installed applications</legend>
  ... <input type="checkbox" class="checkbox" name="items"
             value="my-mammoth-manager" />
      <a href="http://localhost/my-mammoth-manager">
           my-mammoth-manager
           (MammothManager)
        </a>
  ... <legend>Add application</legend>
  ...

Launch the added mammoth manager

  >>> mylink = browser.getLink('my-mammoth-manager (MammothManager)').click()
  >>> print browser.contents
  Let's manage some mammoths!

  >>> print browser.url
  http://localhost/my-mammoth-manager

We are able to delete installed mammoth-mnagers

  >>> browser.open("http://localhost/")
  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ...
  ... <legend>Installed applications</legend>
  ...
  >>> ctrl = browser.getControl(name='items')
  >>> ctrl.getControl(value='my-mammoth-manager').selected = True
  >>> browser.getControl('Delete Selected').click()
  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ...
  ...<legend>Add application</legend>
  ...

"""
import grok

class MammothManager(grok.Application, grok.Container):
    """"A mammoth manager"""
    pass

class Index(grok.View):

    def render(self):
        return u"Let's manage some mammoths!"

"""

=======================================
Basic operations on GrokAdmin instances
=======================================

For the time being, we have the opportunity to add instances of
``GrokAdmin`` using the 'built-in' admin-UI that comes with Grok.

We setup an environment, so that we can simulate through-the-web (TTW)
operations::

   >>> from zope.testbrowser.testing import Browser
   >>> browser = Browser()
   >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
   >>> browser.open("http://localhost/")

The opening screen of the built-in admin-UI provides a possibility to
add a ``GrokAdmin`` instance::

   >>> subform = browser.getForm(name='GrokAdmin')

We create a ``GrokAdmin`` instance called `admin`::
   
   >>> subform.getControl('Name your new app:').value = 'admin'
   >>> subform.getControl('Create').click()

   >>> print browser.contents
   <html xmlns="http://www.w3.org/1999/xhtml">
   ...
   ...<legend>Installed applications</legend>
   ...
   ...<a href="http://localhost/admin">
   ...

"""

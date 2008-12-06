
megrok.login
************

Setting up login pages for your webapp made easy.

:Test-Layer: functional

With `megrok.login` you can setup simple session based login pages
for your ``grok.Application`` and other ``grok.Site`` instances. This
is different to out-of-the-box behaviour, where authentication happens
by basic-auth.

Enabling session based authentication
=====================================

In the most basic form you can declare an application to use login
pages instead of basic-auth like this::

  >>> import grok
  >>> import megrok.login
  >>> class App(grok.Application, grok.Container):
  ...   megrok.login.enable()

Now let's define a view and protect it with a permission::

  >>> class ManageApp(grok.Permission):
  ...   grok.name('app.ManageApp')
  
  >>> class Index(grok.View):
  ...   grok.context(App)
  ...   grok.require('app.ManageApp')
  ...
  ...   def render(self):
  ...     return "Hello from App!"
  ...

Before we can make use of ``megrok.login`` we have to grok it. This
normally happens via ZCML, but here we do it manually::

  >>> import grok.testing
  >>> grok.testing.grok('megrok.login')

Furthermore we have to grok our app components. This normally also
happens at startup::

  >>> from grok.testing import grok_component
  >>> grok_component('App', App)
  True

  >>> grok_component('ManageApp', ManageApp)
  True

  >>> grok_component('Index', Index)
  True

The authentication mechanism needs a site to be plugged in. A Grok
application becomes a site as soon as it is stored in the ZODB. We
do that::

  >>> root = getRootFolder()
  >>> root['app'] = App()

We try to watch the `index` page with a browser. Normally we would get
an error page, as we did not authenticate against the system
before. But this time we are asked to login::

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.open('http://localhost/app')
  >>> browser.headers['status']
  '200 Ok'

  >>> print browser.contents
  <!DOCTYPE html ...
  Please provide Login Information...
  <input type="text" name="login" id="login" />
  ...

What we can see here, is the standard login page provided by
``zope.app.authentication``. It is named `loginForm.html` and the
default, if you do not specify a different viewname as login page.


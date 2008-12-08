
megrok.login
************

Setting up login pages for your webapp made easy.

:Test-Layer: functional

With `megrok.login` you can setup simple session based login pages
for your ``grok.Application`` and other ``grok.Site`` instances. This
is different to out-of-the-box behaviour, where authentication happens
by basic-auth.

Introduction
============

Here we sketch in short, how you can enable simple session based
authentication with ``megrok.login``. More complex examples can
be found in the `tests` subdirectory:

* Basic usage:

 - ``simple.py``:

   How to setup simple(tm) session based authentication with default
   values. This covers the most basic use case.

 - ``customlogin.py``:

   How to setup session based authentication with your own login page.

 - ``autoregister.py``:

   How to setup session based authentication so that users can
   register with the site simply by providing a self-chosen password.

 - ``strict.py``:

   How to setup session based authentication without allowing fallback
   to internal principals which were setup by ZCML at startup.

* More advanced stuff:

 - ``customprincipals.py``:

   How to setup session based authentication with your own
   implementation of principals (users).

 - ``customsession.py``:

   How to setup session based authentication with your own 

 - ``custompausetup.py``:

   How to setup session based authentication with your own setup of
   the ``Pluggable Authentication Utility``.


The ``megrok.login`` directives
===============================

What you can do with ``megrok.login``:


``megrok.login.enable()``
-------------------------

Enables session based authentication. This marker directive *must* be
used in order to use ``megrok.login`` functionality.


``megrok.login.viewname(<viewname>)``
-----------------------------------

Registers the view with the name ``<viewname>`` as login page. This
way you can specify your own login page. You must also use
``megrok.login.enable()`` to make this work.

See ``tests/customlogin.py`` for details.

``megrok.login.strict()``
-------------------------

Normally, ``megrok.login`` installs two authenticator plugins for your
site:

 * a normal ``PrincipalFolder``, that can containn principals (users)
   but is empty in the beginning.

 * a fallback authenticator, that authenticates against the principals
   of the internal principal registry.

If you use ``megrok.login.strict()``, the latter is not installed and
users like the manager user defined in your site.zcml won't be
accepted by your login page.

See ``tests/strict.py`` for details.


``megrok.login.autoregister()``
-------------------------------

If this directive is used, the authentication system will register
automatically any user that still does not exist on login and add it
to the ``PrincipalFolder``.

See ``tests/autoregister.py`` for details.


``megrok.login.setup(<callable>)``
----------------------------------

XXX: not available yet

If you want to setup the Pluggable Authentication Utility (PAU)
yourself, then you can use this directive. It expects a callable as
argument, that will be called with an already created PAU instance as
argument as soon as an application (or other ``grok.Site``) object is
added to the ZODB.

See ``tests/custompausetup.py`` for details.


Setting up session-based authentication
=======================================

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
  >>> grok_component('ManageApp', ManageApp)
  True

  >>> grok_component('App', App)
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


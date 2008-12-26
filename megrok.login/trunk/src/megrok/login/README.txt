
megrok.login
************

Setting up login pages for your webapp made easy.

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

 - ``custompausetup.py``:

   How to setup session based authentication with your own setup of
   the ``Pluggable Authentication Utility``.


The ``megrok.login`` directives
===============================

What you can do with ``megrok.login``:


``megrok.login.enable()``
-------------------------

Enables session based authentication. This marker directive *must* be
used in order to use ``megrok.login`` functionality. It can be set on
any `grok.Site` class::

  import grok
  class MyApp(grok.Application, grok.Container):
    megrok.login.enable()

If no other ``megrok.login`` directive is used, it enables session
based authentication (login screens instead of basic-auth).

``megrok.login.viewname(<viewname>)``
-------------------------------------

Registers the view with the name ``<viewname>`` as login page. This
way you can specify your own login page. You must also use
``megrok.login.enable()`` to make this work::

  import grok
    
  class MyApp(grok.Application, grok.Container):
    megrok.login.enable()
    megrok.login.viewname('login')

  class Login(grok.View):
    def render(self):

    def update(self, camefrom=None, SUBMIT=None):
        self.camefrom=camefrom
        if SUBMIT is not None and camefrom is not None:
            # The credentials were entered. Go back. If the entered
            # credentials are not valid, another redirect will happen
            # to this view.
            self.redirect(camefrom)
        return

whereas the template for the login view might look like this::

  <html>
    <head>
      <title>Login</title>
    </head>
    <body>
      <h1>Custom Login Page</h1>
      <form method="post">
        <div>
  	  <label for="login">Username</label>
          <input type="text" name="login" id="login" />
        </div>
        <div>
          <label for="password">Password</label>
          <input type="password" name="password" id="password" />
        </div>
        <div>
          <input type="hidden" name="camefrom"
                 tal:attributes="value view/camefrom" />
          <input type="submit" name="SUBMIT" value="Log in" />
        </div>
      </form>
    </body>
  </html>

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

Example::

  import grok
  class MyApp(grok.Application, grok.Container):
    megrok.login.enable()
    megrok.login.strict()

See ``tests/strict.py`` for details.


``megrok.login.autoregister()``
-------------------------------

If this directive is used, the authentication system will register
automatically any user that still does not exist on login and add it
to the ``PrincipalFolder``.

Example::

  class ManageApp(grok.Permission):
      grok.name('app.ManageAutoRegister')

  class AutoRegisterApp(grok.Application, grok.Container):
      megrok.login.enable()
      # We grant this permission to autoregistered users.
      megrok.login.autoregister('app.ManageAutoRegister')

See ``tests/autoregister.py`` for details.


``megrok.login.setup(<callable>)``
----------------------------------

If you want to setup the Pluggable Authentication Utility (PAU)
yourself, then you can use this directive. It expects a callable as
argument, that will be called with an already created PAU instance as
argument as soon as an application (or other ``grok.Site``) object is
added to the ZODB.

See ``tests/custompausetup.py`` for details.



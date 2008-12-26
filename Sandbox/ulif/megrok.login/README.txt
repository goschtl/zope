megrok.login
************

Setting up session based login screens for your Grok-based webapps
made easy.

With ``megrok.login`` you can setup a "Pluggable Authentication
Utility" (PAU) automatically, whenever an instance of a
``grok.Application`` is put into the ZODB. The most notable effect is,
that you will have a login screen instead of the basic-auth
authentication when users try to access protected views.

To enable your users to login via a login screen instead of
basic-auth, it is sufficient to create and install an application like
this::

  import grok
  import megrok.login

  class App(grok.Application, grok.Container):
    """An application.
    """
    megrok.login.enable()

See detailed documentation below for details on finetuning
authentication with ``megrok.login``.


Installation
============

1) Add `megrok.login` to the dependencies in your ``setup.py``.

2) Run::

  $ ./bin/buildout

3) Use ``megrok.login`` in your code.

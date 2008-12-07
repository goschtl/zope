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

Using ``megrok.login`` in a Grok project
----------------------------------------

As ``megrok.login`` is not released yet, you have to grab the sources
manually and then register it with buildout.

1) Go to your Grok project root directory::

  $ cd MyProject

2) Get the sources::

    $ svn co svn://svn.zope.org/repos/main/Sandbox/ulif/megrok.login \
        megrok.login

   This will create the sources in your project root.

3) Register the created dir with buildout.

   Edit ``buildout.cfg`` and add ``megrok.login`` at the ``develop``
   entry::

     [buildout]
     develop = . megrok.login
     parts = eggbasket app data zopectl ...
     ....

4) Run buildout::


    $ ./bin/buildout

5) Use ``megrok.login`` in your code::

    
  

1) Add `megrok.login` to the dependencies in your ``setup.py``.

2) Run::

  $ ./bin/buildout

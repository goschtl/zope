ZWiki for Zope 3
================

This product is a port/rewrite of the famous Zope 2 product Zwiki. At
the current stage only the most basic Wiki functionalities are
implemented and much more work needs to be done.


Features
--------

Rendering
~~~~~~~~~

  - Plain Text

  - Structured Text

  - reStructured Text (reST)


Wiki
~~~~

  - Table of Contents

  - Mail Subscription for entire Wiki

  - Full-text Search


Wiki Page
~~~~~~~~~

  - Proper rendering of Wiki Links

  - Edit Wiki Page

  - Preview while editing a page

  - Comment on a Wiki Page

  - Declare Wiki Hierarchy (Parents)

  - Local, WikiPage-based Mail Subscription

  - Jumping to other Wikis


Miscellaneous
~~~~~~~~~~~~~

  - Somewhat sophisticated rendering mechanism. New source types and
    their render methods can now be configured (added) via ZCML.

  - A fully independent skin called 'wiki'; Note that this skin will
    be only useful in the context of a Wiki Page.

Installation
------------

 1. First checkout zwiki source from here::

      svn co svn://svn.zope.org/repos/main/zwiki/trunk zwiki

 2. Run ``bootstrap.py`` from inside folder::

      cd zwiki
      python2.4 bootstrap.py

 3. After bootstraping run ``buildout`` command::

      ./bin/buildout

 4. Firnally to run wiki application, execute ``instance`` script::

      ./bin/instance fg

 5. Now open http://localhost:8080/manage, use 'admin' as username
    and 'admin' as password.  Add wiki instance by clicking in the left
    menu item for wiki adding.

 6. After adding wiki, you can access wiki from: 
    http://localhost:8080/++skin++wiki/Wiki/FrontPage

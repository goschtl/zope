ZWiki for Zope 3
================

This product is a port/rewrite of the famous Zope 2 product Zwiki. At
the current stage only the most basic Wiki functionalities are
implemented and much more work needs to be done.

Features
--------

Rendering

  - Plain Text

  - Structured Text

  - reStructured Text (reST)


Wiki

  - Table of Contents

  - Mail Subscription for entire Wiki

  - Full-text Search


Wiki Page

  - Proper rendering of Wiki Links

  - Edit Wiki Page

  - Comment on a Wiki Page

  - Declare Wiki Hierarchy (Parents)

  - Local, WikiPage-based Mail Subscription

  - Jumping to other Wikis


Miscellaneous

  - Somewhat sophisticated rendering mechanism. New source types and
    their render methods can now be configured (added) via ZCML.

  - A fully independent skin called 'wiki'; Note that this skill will
    be only useful in the context of a Wiki Page.

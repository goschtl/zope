============
CMF.buildout
============
-------------------------
Build CMF 2.2 + Zope 2.12
-------------------------

Introduction
============

Builds CMF 2.2 with Zope 2.12 from develop eggs located in ``src``.

Dependencies
============

Requires Python 2.4 or 2.5.

Usage
=====
::

  $ python2.5 bootstrap/bootstrap.py
  $ ./bin/buildout
  $ ./bin/test
  $ ./bin/instance start

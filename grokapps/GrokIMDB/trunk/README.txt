********
GrokIMDB
********

This is a nifty little demo application for Grok.

It provides a userinterface to fetch and edit data retrieved from the
Internet Movie Database (IMDb).

Prerequisites
=============

You need 

  - Python 2.4 and 

  -`setuptools` 

to run this application. Rumors are, that also Python 2.5 will work.


Installation
============

To install this package, run::

  $ bootstrap/bootstrap.py

which should create a `bin/` directory containing a `buildout` script.

Next, run::

  $ bin/buildout

which should setup everything, fetch needed packages from the net
etc.


Run the Application
===================

This can be done in three steps.


1) Start the Zope-Server
------------------------

To start the application in the background, run::

  $ bin/zopectl start

and stop it with::

  $ bin/zopectl stop

Tests are run doing::

  $ bin/test

If you want to run the application in foreground, you can do::

  $ bin/zopectl fg

The server can then be stopped hitting CTRL-D.


2) Log into the admin interface
-------------------------------

One server can serve several instances of GrokIMDB. Therefore we
firstly have to create an instance of it. To do this, we use the Grok
admin interface, which can be reached via::

  http://localhost:8080/

Open that URL in a browser. You will be asked for a username/password.

Enter::


  grok

and

  grok

That should log you in.


3) Create an instance of GrokIMDB
---------------------------------

Now enter a name for your new GrokIMDB instance and click 'Add'. This
should create a new instance of GrokIMDB, that will be displayed.

To go to your new GrokIMDB, just click on the freshly created link.


Development
===========

GrokIMDB can give you only a rough sketch of all possibilities of
Grok. You can develop the application further by modifying the sources
in the `src/` directory. Note, that you have to restart the server,
when classes or similar things were changed.


Further Grok Resources
======================

There is an excellent tutorial on the Grok homepage::

  http://grok.zope.org/documentation/book/


Happy Grokking!


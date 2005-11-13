================
Online Tutorials
================

We have recently started to write our functional doctests using the
``zope.testbrowser`` package. The advantage of using the testbrowser is, of
course, that we are describing the real interaction of the user with the
browser. This does not only provide much nicer documentation, but also
provides us with additional information about the usage of the Web
application.

Let's imagine we could use those documentation files to create fully generated
tutorials. This package provides the necessary framework to run testbrowser
tests inside a real browser in a tutorial style:

  >>> from zope.tutorial import tutorial, manager

Tutorial
--------

Each doctest file that you wish to be available as a tutorial is represented
by the `Tutorial` class.


Tutorial Manager
----------------

All tutorials are managed by the tutorial manager, which also serves as an
entrance point in the Web UI.

  >>> tm = manager.TutorialManager()

The tutorial manager implements the `IReadContainer` interface to query for
tutorials. Initially there are no tutorials:

  >>> tm.keys()
  []

Once we add some tutorials by registering soem utilities,

  >>> import zope.component

  >>> tut1 = tutorial.Tutorial('Tutorial 1', 'tut1.txt')
  >>> zope.component.provideUtility(tut1, name='tut1')

  >>> tut2 = tutorial.Tutorial('Tutorial 2', 'tut2.txt')
  >>> zope.component.provideUtility(tut2, name='tut2')

we have some results:

  >>> tm.items()
  [(u'tut1', <Tutorial title='Tutorial 1', file='tut1.txt'>),
   (u'tut2', <Tutorial title='Tutorial 2', file='tut2.txt'>)]


`++tutorials++` Namespace
-------------------------

For URLs and TALES expression, a namespace is provided that provides you with
an entrance point to the tutorial application. Once the namespace is created.

  >>> parent = object()
  >>> namespace = manager.tutorialsNamespace(parent)

you can traverse the parent to the tutorial manager. If an empty name is
passed into the namespace, the manager is returned:

  >>> namespace.traverse('')
  <zope.tutorial.manager.TutorialManager object at ...>

If a name is provided, then the actual tutorial is looked up:

  >>> namespace.traverse('tut1')
  <Tutorial title='Tutorial 1', file='tut1.txt'>

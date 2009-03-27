======================================
The Zope 3 Community's Project Builder
======================================

z3c.builder is a tool that helps you jump start development of a Zope
3 application by generating all the boiler plate code and
configuration for you.

Goals
-----

 * Easy to use
 * Easy to extend
 * More or less complete


Brainstorming
-------------

The easiest thing to tackle is just generating all the files that are
needed without necessarily any customizable contents.  A minimal eggs
and buildout based project would have a directory structure like this::

  package-name/
    bootstrap.py
    buildout.cfg
    setup.py
    README.txt
    CHANGES.txt
    src/
      namespace-package/
        __init__.py
        package/
          __init__.py

Each section of this directory structure can be further configured ad
infinitum.  The tricky part is deciding when enough is enough.  Let's
consider each of these sections and what they offer.

bootstrap.py
~~~~~~~~~~~~

This is brain dead simple.  There is a standard file that everyone
uses and we just need to copy it in.  I don't think there is any
potential customization points.


buildout.cfg
~~~~~~~~~~~~

There are pretty much an infinite number of generic customizations you
can make to a buildout.cfg file.  Here are some of the ones we might
want to support out of the box:

  - Creation of multiple buildout.cfg files, for different uses
    (developers, production, minimal?)

  - kgs hookup, with support for using a remote extends buildout
    option, or downloading a versions.cfg file upon project creation.

  - Some typically used and useful parts:
    - tests
    - coverage
    - python interpreter
    - ctags
    - documentation generators

    (note that some of these parts require additional files to be
     added to the src tree in order to make sense)

  - Zope Server setup.
    This bleeds into all the zope 3 configuration that we might
    want to do and also paster setup.  This would include basically
    anything you can configure in zope.conf files.

setup.py
~~~~~~~~

This is relatively straight forward.  There are the obvious keyword
arguments that are passed to the setup() command that we'll want to
configure. There are however some slightly more interesting peices:

  - long_description: Since this is what becomes the python page,
    we'll want to hook up the boiler plate code for using a
    combination of README.txt, CHANGES.txt and others to generate the
    full long description.  This shouldn't be that hard.

  - classifiers: It's always a pain in the ass to remember what all
    the different classifiers can be and how they should be
    formatted.

  - extras_requires: we may want to configure what extras_requires
    sections there are.  Typically we would have a test and an app
    section. There might also be a docs section and others.

  - entry_points: this is where it gets a bit trickier.  Paster has
    it's own entry point boiler plate code that you need.  We may also
    want to configure any number of additonal command line script
    entry points.

README.txt
~~~~~~~~~~

Just a simple file dump with maybe some configurable initial content.

CHANGES.txt
~~~~~~~~~~~

Another simple file dump with an example of the change log format that
we've standardized on.

Other Python Files
~~~~~~~~~~~~~~~~~~

The rest of the files are just for mkaing proper python modules and
should be brain dead simple.

Conclusion
~~~~~~~~~~

I think starting by making a project builder for simple egg/buildout
based projects is a good starting point.  It's an atainable and useful
goal which will give us the experience we need to tackle the more
complex task of zope boiler plate.

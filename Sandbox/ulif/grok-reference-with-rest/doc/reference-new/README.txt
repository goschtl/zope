=========================
The grok reference manual
=========================

The manual is written using ReStructured Text (ReST) with support for
the Python documentation markup. The ReST sources can be compiled into
HTML. To build the manual, you need some special tools described
below.

The current documents were converted from LaTeX to ReST using Georg
Brandls converter.py tool, which is part of the current doctools
trunk. You can find it here::

   http://svn.python.org/projects/doctools/trunk/


Hints for documentation writers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As the format was switched from LaTeX to ReST, you might want to read
some hints about the changed notation of entities. Please read::

   http://docs.python.org/dev/documenting/fromlatex.html

to learn more about the differences. General information about the
markup can be found here::

   http://docs.python.org/dev/documenting/index.html


Build the HTML
~~~~~~~~~~~~~~

Prerequisites:
--------------

The HTML is generated basically by the new sphinx package in
docutils. This *requires*:

 * Python >= v2.5

 * docutils >= v0.4

*Optional* you can install pygments for syntax highlithing.

Basically, it should be sufficient, to check out sphinx and other
helper tools from the docutils subversion repository::

  $ cd doc/
  $ svn co svn co http://svn.python.org/projects/doctools/trunk/ ref-tools

Checking out in the ``reference`` directory itself will cause trouble,
so do it in the ``doc`` or another directory, which will not be parsed for
rst files.

The current docutils tool-chain is pretty focused on Python
documentation, including the original Python directory structure and
other things more specific for Python documentation. I believe, that
this will change but currently you have to tweak the original sources
a bit, to run with other documentation.

To generate Grok reference (and not pure Python documentation), the
tools can be patched with the patch provided in ``reference/``.

  $ patch -p0 ref-tools < reference/ref-tools.diff

The patch applies some changes to leave the index page untouched and
to display Grok as project name.


Compiling the sources into HTML::
---------------------------------

Create a target directory::

  $ mkdir ref-build

and compile the ReST sources:

  $ python2.5 ref-tools/sphinx-build.py -b html reference/ ref-build


The build process is subject to change. The format will stay.



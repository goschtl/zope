=======
grokref
=======

Generate reference documentation in various formats from ReStructured
Text (ReST) sources.

What is so special about grok reference documentation?
------------------------------------------------------

The grok reference documentation can be found in the `doc/reference`
subdirectory of every source distribution of Grok. The sources can be
fetched online from http://svn.zope.org/grok/doc/reference.

The reference consists of a set of ReStructured Text source files.

It is special, because some 'tags' are used, that are not supported by
standard Python ``docutils``. The ``docutils`` package is a tool to
create HTML and other output formats from ReST.

In the reference are roles and directives used, that are used also in
the standard Python source code documentation (starting with Python
2.6) but not in the standard ``docutils`` package. Unfortunately, the
``sphinx`` package, which is part of the standard Python toolchain,
currently only supports the Python source code tree for generation of
HTML and other output. Directory names are hardcoded and everything
needs at least Python 2.5 to generate reference documentation with the
``sphinx`` package.


What is the purpose of ``grokref``?
-----------------------------------

``grokref`` is a package to add support for the special roles and
directives mentioned above but without the need to use the sphinx
package. It allows generation of the Grok reference manual in HTML and
PDF (LaTeX) format.

It is written in a way, so that other references could be generated as
well.

Grokref tries to provide the full set of roles and directives as is
provided by the standard Python documentation. The output, however,
will be different from what you might expect, if you have seen the
``sphinx`` output before.


How can I generate HTML from the ReST sources?
----------------------------------------------

After running ``buildout`` in the grok ``bin`` directory, there should
be a new script called ``grokref2html``. This script can be called
with a ReST source file as argument::

   $ bin/grokref2html doc/reference/index.rst

This will ouput HTML to the commandline (subject to change).

Run::

   $ bin/grokref2html --help

for a complete list of available options.



How do I write reference documentation?
---------------------------------------

Just write normal ReST sources.

You can (and should) use the following additional roles and directives
to better describe the things you describe:


Additional value substitutions:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following keys can be used in reference documents by enclosing
them in pipe characters (`|`). They will be substituted by values
defined in the ``ReferenceProducer``.

* ``version``:

  The version of grok that is documented.

* ``release``:

  The release that is documented.

* ``today``:

  The date of today.


Additional directives:
~~~~~~~~~~~~~~~~~~~~~~

* ``function``:

  To describe functions and methods with their signature.


Additional roles (general):
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* `attr`:

  To describe an attribute of a class/instance.

* `class`:

  To describe a class.

* `const`:

  To describe a constant.

* `data`:

  ???

* `exc`:

  To describe an exception.

* `file`:

  To describe a file.

* `func`:

  To describe a function.

* `meth`:

  To describe a method of a class.

* `mod`:

  To describe a module/package name.

* `ref`:

  ???

* `samp`:

  ???

* `term`:

  ???

* `token`:

  ???

Additional roles (C-related):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* `cdata`:

  ???

* `cfunc`:

  A function written in C.

* `cmacro`:

  A macro defined in C.

* `ctype`:

  A type defined/declared in C.



Customized parsers and writers
------------------------------

Grokref provides already customized parsers and writers from the
``docutils`` point of view. 

If you want to write an own HTML writer for example, it should be
sufficient to include the roles and directives from the ``extensions``
directory.

Note, that you also need a ``translator`` to translate the special
entitites supported by grokref into your special output format. Some
examples can be found in ``translators.py`` in the `extensions`
directory.


=======
grokref
=======

Generate reference documentation in various formats from ReStructured
Text (ReST) sources.


The grok reference documentation can be found in the `doc/reference`
subdirectory of every source distribution of Grok. The sources can be
fetched online from http://svn.zope.org/grok/doc/reference.

The reference consists of a set of ReStructured Text source files.


How can I generate HTML from the ReST sources?
----------------------------------------------

After running ``buildout`` in the grok ``bin`` directory, there should
be a new script called ``grokref2html``. This script can be called
with a source directory as argument::

   $ bin/grokref2html doc/reference

This will ouput HTML files (one for each .rst file found in the
directory) in the source directory.

To generate the output in a different directory, just pass the target
directory as additional parameter::

   $ bin/grokref2html doc/reference ~/targetdir

The destination directory must exist before.

There are plenty of options for the reference building process, which
are listed, if you run::

   $ bin/grokref2html --help

for a complete list of available options.



How do I write reference documentation?
---------------------------------------

Just write normal ReST sources.

Primers for writing restructured text documents are available at

  http://docutils.sourceforge.net/rst.html

and::

  http://docs.python.org/dev/documenting/rest.html

The document you are reading, is a ReST file as well, of course.

You can (and should), however, use the following additional roles and
directives to better describe the things you describe:


Substitutions, Roles and Directives supported by grokref:
---------------------------------------------------------

The following roles, directives and substitutions are supported by
grokref but not by the standard docutils tools.

Additional Default Substitutions:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Substitutions in the `doctools` sense are keywords, which are written
enclosed in pipe characters (`|`) in ReST sources and which are
replaced by certain values during parsing and document generation. You
can therefore think of substitutions as of placeholders.

Typical substitutions are `date`, `time` and `version`. Unfortunately,
the values of those substitutions are not defined by default and its
use leads to errors and warnings.

To define a substitution, you can use ReST as shown on:

  http://docutils.sourceforge.net/docs/ref/rst/substitutions.html

If you use a `ReferenceReader` from the `grokref.grok2html` modules,
the following substitutions are set.

You can also use an instance of ``ReferenceProducer`` (which uses
`ReferenceReader` by default) and set the instances `version`,
`release` and `today` attributes, whose values will then show up in
the generated documents.

* ``version``:

  The version of grok that is documented. For example `0.11`.

* ``release``:

  The release that is documented. For example `0.11a`.

* ``today``:

  The date of today, i.e. the day you generate documentation.


Additional directives:
~~~~~~~~~~~~~~~~~~~~~~

Directives are written in ReST sources with a directive name followed
by two semicolons. Normally they are preceeded by two dots and a
space. Directives define a special 'environment', to mark the
following text (as long as it is indented) as one compound
unit. 

Typical directives (provided by the standard `docutils`) include
`caution` to mark a block of text with warnings, `note`, `image` or
`sidebar`. Usually directives mark complete blocks of text, while
roles only mark one or a few words. If you want to mark the word
`myfunc` as a function, use a role. If you want to describe the
function extensively, with all parameters and return values, use a
directive.

Directives not provided by standard `docutils` but by `grokref` and
`sphinx`:

Python Directives
+++++++++++++++++

* ``attribute``:

  To describe an attribute of a class.

* ``class``:

  To describe a Python class.

* ``data``:

  To describe some data extensively.

* ``exception``:

  To describe an exception type.

* ``function``:

  To describe functions with their signature.

* ``method``:

  To describe a class method.

Generic Directives 
++++++++++++++++++

* ``cmdoption``:

  To describe command options of a program.

* ``envvar``:

  To describe environment variables.

* ``decribe``:

  To describe something that describes something.


Special Directives:
+++++++++++++++++++

* ``toctree``:

  Currently disabled.

  The `toctree` directive creates a table of contents of given ReST
  files, which are given as arguments. A typical toctree definition
  might look like this::

    .. toctree::
       :maxdepth: 2

       file1.rst
       file2.rst
       foo.rst

  The option `maxdepth` (default: 0 == no limit)
  determines the maximum depth of the toctree to be generated.

  The filename entries will then be replaced by the headings (TOCs) of
  the appropriate files.

  .. note::

    This directive is currently accepted by grokref, but not
    processed. A toctree will therefore not show up in your documents.

* ``seealso``:

  This directive works like a `note` or `caution` amonition. There is
  no special handling of references in `seealso`` directives.

* ``versionadded``:

  This directive indicates, that something was added during a certain
  release. 

  It requires a version number as first argument and prints then the
  rest of the contents.

  A typical usage would be::

    .. versionadded:: 0.12

    Added in version 0.12. Don't use clubs in prior versions.

* ``versionchanged``:

  This directive indicates, that something (especially a signature or
  similar) changed during version changes. See ``versionadded``.

* ``deprecated``:

  This directive indicates, that something, a function, class or
  similar, is deprecated. It also requires a version number and an
  explanatory text.

  See ``versionadded`` for details.


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


Python
======

The general rule when writing Python code is to follow PEP 8. The rules
given below override what is said in `PEP 8`_.

.. note::
    Please be aware that PEP 8 recommends module-level consistency over blind
    rule-following. Zope 3 has been around for a while and older code may have
    been written with a different set of rules.
    modules might not match the current rules. In that case, please make a
    conscious decision about a reasonable level of consistency.


License statement and module docstring
--------------------------------------

Python files should always contain the most actual license comment at the top followed by the
module documentation string.

The docstring will contain a reference about version control status. The
example given is valid for at least CVS and Subversion.

Here is the template::

  ##############################################################################
  #
  # Copyright (c) 2009 Zope Corporation and Contributors.
  # All Rights Reserved.
  #
  # This software is subject to the provisions of the Zope Public License,
  # Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
  # THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
  # WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
  # WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
  # FOR A PARTICULAR PURPOSE
  # 
  ##############################################################################
  """One-line summary goes here.

  Module documentation goes here.

  $Id$
  """

.. note::
    TODO We never finished discussing license years. When should the
    license year be updated? Do we have to enumerate individual years or
    is it ok to give ranges?

    Guido (around 2002) pointed out the FSF's rules. Those should be
    re-evaluated.

    Efge pointed out that in the US only the first year of publication needs to be given. (See http://www.loc.gov/copyright/circs/circ03.html).

    This also points out that we need an understanding of when code is
    published the first time. Can checking into a public repository can
    count as published? The FSF seemed to understand inclusions in
    release tarballs as publications.

Interfaces
----------

Interface names adhere to PEP 8's naming of classes, except that they
are prefixed with a capital ``I``, as in ``IMagicThing``.

One function of interfaces is to document functionality, so be very
verbose with the documentation strings.

All public interfaces should go into a file called ``interfaces.py``.
"Public" interfaces are those that you expect to be implemented more
than once. Interfaces that are likely to be implemented only once, like
``IGlobalAdapterService``, should live in the same module as their
implementation.

.. note::
    TODO clarify whether the single/multiple implementation rule holds.

    TODO there has been discussion about whether imperative or
    present tense is to be preferred for describing interfaces. The
    discussion was not resolved.

Attribute and method names
--------------------------

The naming of attributes as recommended by PEP 8 is controversial. PEP 8
prefers ``attribute_name`` over ``attributeName``. Newer code tends to
prefer the use of underscores over camel case. However, Zope 3 has been
built originally with the latter rule and a lot of code still use this
meme.

Boolean-type attributes should always form a true-false-question,
typically using "has" or "is" as prefix. Example: ``is_required`` instead
of ``required``.

Method names should always start with a verb that describes the action.

Examples::

    good:
    first_name
    is_required
    execute_command()
    save()
    convert_value_to_string()

    bad:
    FirstName
    required
    command()
    string()


.. note::
    TODO This rule needs clarification.


Global variable names
---------------------

Public global variables names are spelled with CapitalizedWords, as in
``Folder`` or ``RoleService``.

An exception is made for global non-factory functions, which are
typically spelled with ``mixedCase``.

.. note::
    TODO This rule needs clarification.


Avoid single-letter variables
-----------------------------

Single-letter variable names should be avoided unless:

 - Their meaning is extremely obvious from the context, and

 - Brevity is desireable

The most obviouse case for single-letter variables is for iteration
variables.


Imports
-------

All imports should be at the top of the module, after the module
docstring and/or comments, but before module globals.

It is sometimes necessary to violate this to address circular import
pronlems. If this is the case, add a comment to the import section at
the top of the file to flag that this was done.

Order your imports by simply ordering the lines as `sort` would. Don't
create blocks of imports with additional empty lines as PEP 8 recommends.

.. note::
    TODO This rule has been recommended by Jim but hasn't been
    officially established.


Refrain from using relative imports.  Instead of::

    import foo # from same package

you can write::

    from Zope.App.ThisPackage import foo

.. note::
    TODO Clarify, clean up wording. I think we also avoid re-imports of
    symbols and most times prefer the ``import`` over the ``from`` form.

    Relative imports should be avoided, I'm not sure about the style 
    once we start getting real relative imports from Python.

Catch specific errors, write small ``try`` blocks
-------------------------------------------------

If you are converting a value to an ``int``, and you want to catch
conversion errors, you need only catch ``ValueError``. Be sure to do the
minimum possible between your ``try:`` and ``except ValueError:``
statements.


Don't leave trailing whitespace
-------------------------------

Trailing whitespace should not occur, nor should blank lines at the end
of files.


Be tolerant
-----------

Be tolerant of code that doesn't follow these conventions. We want to
reuse lots of software written for other projects, which may not follow
these conventions.

A reasonable goal is that code covered by the ZPL should follow these
conventions.


.. _`PEP 8`: http://www.python.org/dev/peps/pep-0008/

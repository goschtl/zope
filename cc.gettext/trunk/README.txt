***********************
Buildout GetText Recipe
***********************

.. contents::

cc.gettext provides recipe[s] for manipulating gettext message catalogs.

Compiling gettext catalogs
==========================

The cc.gettext:msgfmt recipe can be used to compile gettext catalogs from
the .po source format to the binary .mo representation needed by Zope 3.
It supports two options:

po_path
    A file path (relative to the buildout base or absolute) which is scanned
    recursively for .po files.  All .po files found are processed by the 
    recipe.

mo_path
    The base file path (relative to the buildout base or absolute) where
    compiled .mo files are written.  Compiled files are named using the 
    pattern <mo_path>/<locale>/LC_MESSAGES/<domain>.mo

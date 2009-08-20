Introduction
************

This recipe can be used to generate directories.

A short example::

  [buildout]
  parts = var

  [var]
  recipe = z3c.recipe.mkdir

This will create a directory named ``var/`` in the buildout ``parts/``
directory. If you want a different path, you can set the ``paths``
option::

  [buildout]
  parts = foo

  [foo]
  recipe = z3c.recipe.mkdir
  paths = foo/bar

which will create 'foo/bar/' in the buildout root directory (not the
``parts/`` directory). Also intermediate directories are created (if
they do not exist).

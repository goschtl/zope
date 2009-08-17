Detailed Description
********************

Simple creation of directories via buildout
===========================================

Lets create a minimal `buildout.cfg` file::

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... ''')

Now we can run buildout::

  >>> print system(join('bin', 'buildout')),
  Installing mydir.

The directory was indeed created in the ``parts`` directory::

  >>> ls('parts')
  d  mydir

As we did not specify a special path, the name of the created
directory is like the section name ``mydir``.


Creating a directory in a given path
====================================

Lets create a minimal `buildout.cfg` file. This time the directory
has a name different from section name and we have to tell explicitly,
that we want it to be created in the ``parts/`` directory:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... path = ${buildout:parts-directory}/myotherdir
  ... ''')

Now we can run buildout::

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.

The directory was indeed created::

  >>> ls('parts')
  d  myotherdir


Creating relative paths
=======================

If we specify a relative path, this path will be read relative to the
buildout directory:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... path = myrootdir
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.

  >>> ls('.')
  -  .installed.cfg
  d  bin
  -  buildout.cfg
  d  develop-eggs
  d  eggs
  d  myrootdir
  d  parts

  The old directory will vanish:

  >>> ls('parts') is None
  True


Creating intermediate paths
===========================

If we specify several levels of directories, the intermediate parts
will be created for us as well:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... path = myrootdir/other/dir/finaldir
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.

  >>> ls('myrootdir', 'other', 'dir')
  d  finaldir

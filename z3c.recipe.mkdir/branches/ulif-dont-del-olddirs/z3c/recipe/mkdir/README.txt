Detailed Description
********************

.. contents::


Recipe Options
==============

``z3c.recipe.mkdir`` provides the following options:

* ``paths``
    Contains the path(s) of directories created in normalized,
    absolute form. I.e.:: 

      mydir/../foo/bar

    becomes::

      /path/to/buildout-dir/foo/bar

* ``remove-on-update``
     Default: ``no``

     By default, created directories are not removed
     on updates of buildout configuration. This is a security measure
     as created directories might contain valuable data.

     You can, however, enforce automatic removing on updates by
     setting this option to ``on``, ``yes`` or ``true``.


Simple creation of directories via buildout
===========================================

Lets create a minimal `buildout.cfg` file:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... ''')

Now we can run buildout:

  >>> print system(join('bin', 'buildout')),
  Installing mydir.
  mydir: created path: /sample-buildout/parts/mydir

The directory was indeed created in the ``parts`` directory:

  >>> ls('parts')
  d  mydir

As we did not specify a special path, the name of the created
directory is like the section name ``mydir``.


Creating a directory in a given path
====================================

Lets create a minimal `buildout.cfg` file. This time the directory
has a name different from section name and we have to tell explicitly,
that we want it to be created in the ``parts/`` directory. We set the
``paths`` option to do so:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... paths = ${buildout:parts-directory}/myotherdir
  ... ''')

Now we can run buildout:

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.
  mydir: created path: /sample-buildout/parts/myotherdir

The directory was indeed created:

  >>> ls('parts')
  d  mydir
  d  myotherdir


Creating directories that are removed on updates
================================================

We can tell, that a directory should be removed on updates by using
the ``remove-on-update`` option:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... remove-on-update = true
  ... paths = newdir
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.
  mydir: created path: /sample-buildout/newdir

The ``newdir/`` directory was created:

  >>> ls('.')
  -  .installed.cfg
  d  bin
  -  buildout.cfg
  d  develop-eggs
  d  eggs
  d  newdir
  d  parts

We rewrite `buildout.cfg` and set a different path:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... remove-on-update = true
  ... paths = newdir2
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.
  mydir: created path: /sample-buildout/newdir2

Now ``newdir/`` has vanished and ``newdir2`` exists:

  >>> ls('.')
  -  .installed.cfg
  d  bin
  -  buildout.cfg
  d  develop-eggs
  d  eggs
  d  newdir2
  d  parts

Note, that the created directory will be removed on next modification
of `buildout.cfg`.


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
  ... paths = myrootdir
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.
  mydir: created path: /sample-buildout/myrootdir


  >>> ls('.')
  -  .installed.cfg
  d  bin
  -  buildout.cfg
  d  develop-eggs
  d  eggs
  d  myrootdir
  d  parts

  The old directories will **not** vanish:

  >>> ls('parts')
  d  mydir
  d  myotherdir


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
  ... paths = myrootdir/other/dir/finaldir
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.
  mydir: created path: /sample-buildout/myrootdir/other/dir/finaldir

  >>> ls('myrootdir', 'other', 'dir')
  d  finaldir


Paths are normalized
====================

If we specify a non-normalized path (i.e. one that contains references
to parent directories or similar), the path will be normalized before
creating it:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... paths = myroot/foo/../dir1/../bar/.
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.
  mydir: created path: /sample-buildout/myroot/bar

Only ``bar/`` will be created:

  >>> ls('myroot')
  d  bar


Creating multiple paths in a row
================================

We can create multiple paths in one buildout section:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... paths = myroot/dir1
  ...         myroot/dir2
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.
  mydir: created path: /sample-buildout/myroot/dir1
  mydir: created path: /sample-buildout/myroot/dir2


  >>> ls('myroot')
  d  bar
  d  dir1
  d  dir2

Note, that in this case you cannot easily reference the set path from
other recipes or templates. If, for example in a template you
reference::

  root_dir = ${mydir:path}

the result will become::

  root_dir = /path/to/buildout/dir1
  path/to/buildout/dir2

If you specify only one path, however, the second line will not appear.

Use several sections using `z3c.recipe.mkdir` if you want to reference
different created paths from templates or similar.


Trailing slashes do not matter
==============================

It doesn't matter, whether you specify the paths with trailing slash
or without:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... paths = myroot/dir3/
  ...         myroot/dir4
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.
  mydir: created path: /sample-buildout/myroot/dir3
  mydir: created path: /sample-buildout/myroot/dir4

  >>> ls('myroot')
  d  bar
  d  dir1
  d  dir2
  d  dir3
  d  dir4

Things to be aware of
=====================

If you change the setting of some path, the old directory and all its
contents will **not** be deleted (as you might expect from a buildout
recipe):

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... paths = path1
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.
  mydir: created path: /sample-buildout/path1

  >>> write(join('path1', 'myfile'), 'blah\n')
  >>> ls('path1')
  -  myfile

Now we switch the setting of mydir to ``path2``:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... paths = path2
  ... ''')

  >>> print system(join('bin', 'buildout'))
  Uninstalling mydir.
  Installing mydir.
  mydir: created path: /sample-buildout/path2
  <BLANKLINE>

The file we created above is still alive:

  >>> ls('path1')
  -  myfile


Things, one should not do
=========================

Trying to create directories that exist and are files
-----------------------------------------------------

If a part of a given path already exists and is a file, an error is
raised:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... paths = rootdir2/somefile/foo
  ... ''')

Now we create the first part of the path beforehand:

  >>> import os
  >>> os.mkdir('rootdir2')

And make the second part of the path a file:

  >>> write(join('rootdir2', 'somefile'),
  ... '''
  ... blah
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.
  While:
    Installing mydir.
  Error: Cannot create directory: /.../rootdir2/somefile. It's a file.


Don't use ``path`` option
-------------------------

.. note:: ``path`` is deprectated!

Starting with version 0.3 the ``path`` option is deprecated. Use
``paths`` instead:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... path = myrootdir
  ... remove-on-update = yes
  ... ''')

  >>> print system(join('bin', 'buildout')),
  mydir: Use of 'path' option is deprectated. Use 'paths' instead.
  Installing mydir.
  mydir: created path: /sample-buildout/parts/mydir

The ``path`` option will be supported only for a limited time!



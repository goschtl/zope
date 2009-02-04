
Supported options
=================

The recipe supports the following options:

path
    The directory, where the generated text files should be
    placed. Default is the local buildout directory.

<file.name>
    A textfile to create. Creates a file named ``file.name`` with the
    option's value as content. Substitutions like
    ${buildout:directory} are performed in the resulting file.

    To make this happen, the filename must contain a dot and must not
    end with ``-template``.

    If you define a ``<file.name>`` option, you must not define a
    ``<file.name>-template`` option.

<file.name>-template 
    A path to a template. 

    Instead of passing the contents of the file to create as option
    value, you can also name a template file. 

    Substitutions like ${buildout:directory} are performed in the
    resulting file.

    This would result in a file ``file.name`` created in the ``path``
    directory with (substituted) contents read from the template file
    specified by this option.

You can specify as many ``<file.name>`` and ``<file.name>-template``
options as you like.


Example usage
=============

Specifying a file to create
---------------------------

We start by creating a buildout that uses the recipe::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = conffiles
    ...
    ... [conffiles]
    ... recipe = z3c.recipe.textfile
    ... myconf.txt = Hello from myconf.txt
    ... """)

By setting an option ``myconf.txt`` we indicate, that we want to
create a file ``myconf.txt`` with contents ``Hello from myconf.txt``.

Running the buildout gives us::

    >>> print 'start', system(buildout) # doctest:+ELLIPSIS
    start...
    Installing conffiles.
    conffiles: Creating file myconf.txt

We now have a file ``myconf.txt``::

    >>> ls('.')
    -  .installed.cfg
    ...
    -  myconf.txt
    ...

The freshly created file indeed provides the contents given above::

    >>> cat('myconf.txt')
    Hello from myconf.txt


Specifying where textfiles should be created
--------------------------------------------

By default files are created in the local buildout root.

When we give a ``path``-option in our ``buildout.cfg``, the file will
be created in this location::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = conffiles
    ...
    ... [conffiles]
    ... recipe = z3c.recipe.textfile
    ... path = etc
    ... myconf.txt = Hello from myconf.txt
    ... """)

    >>> print 'start', system(buildout) # doctest:+ELLIPSIS
    start...
    Installing conffiles.
    conffiles: Creating directory etc
    conffiles: Creating file myconf.txt

Now also the ``etc/`` directory was created for us::

    >>> ls('etc')
    -  myconf.txt

The contents of the text file is still the same::

    >>> cat('etc', 'myconf.txt')
    Hello from myconf.txt


Substitutions in generated text files
-------------------------------------

To make real use of automatically generated text files you can use
substitutions, so that variables from other recipes can be filled in::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = conffiles
    ...
    ... [conffiles]
    ... recipe = z3c.recipe.textfile
    ... myconf.txt = project_root: ${buildout:directory}
    ... """)

    >>> print 'start', system(buildout) # doctest:+ELLIPSIS
    start...
    Installing conffiles.
    conffiles: Creating file myconf.txt

The term ``${buildout:directory}`` above will be substituted by the
real path of our buildout environment::

    >>> cat('myconf.txt')
    project_root: .../sample-buildout

You can use any option that is referencable for buildout. Also options
defined in our ``[conffiles]`` section (which can be named as you
like), can be used::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = conffiles
    ...
    ... [conffiles]
    ... recipe = z3c.recipe.textfile
    ... somekey = someValue
    ... myconf.txt = project_root: ${buildout:directory}
    ...              important_val: ${conffiles:somekey}
    ... """)

    >>> print 'start', system(buildout) # doctest:+ELLIPSIS
    start...
    Installing conffiles.
    conffiles: Creating file myconf.txt

    >>> cat('myconf.txt')
    project_root: /sample-buildout
    important_val: someValue

There will happen no other substitutions than replacing buildout-vars.

This can be handy when using external template files.


Using template files
--------------------

Instead of giving the contents of files to be created directly in
``buildout.cfg``, you can also create template files, which are parsed
on buildout runs, references substituted and then written to the
created files.

We create a template file, this time like an .ini-file::

    >>> write('myconf_template',
    ... """
    ... [project_root]
    ... ${buildout:directory}
    ...
    ... [sources]
    ... ${buildout:directory}/src
    ...
    ... """)

If we want a file ``myconf.ini`` to be created out of this template,
we have to use the syntax ``<file.name>-template``, where
``<file.name>`` is an arbitrary filename containing at least a dot::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = conffiles
    ...
    ... [conffiles]
    ... recipe = z3c.recipe.textfile
    ... somekey = someValue
    ... myconf.ini-template = myconf_template
    ... """)

    >>> print 'start', system(buildout) # doctest:+ELLIPSIS
    start...
    Installing conffiles.
    conffiles: Creating file myconf.ini

    >>> cat('myconf.ini')
    <BLANKLINE>
    [project_root]
    /sample-buildout
    <BLANKLINE>
    [sources]
    /sample-buildout/src
    <BLANKLINE>


There is only one way to pass a text file's content
---------------------------------------------------

If we give two options which would both concern the same file to be
generated, the recipe refuses to guess.

Here we request to create a file ``myconf.ini`` two times. This is not
allowed::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = conffiles
    ...
    ... [conffiles]
    ... recipe = z3c.recipe.textfile
    ... myconf.ini-template = myconf_template
    ... myconf.ini = The file contents
    ... """)

    >>> print system(buildout) # doctest:+ELLIPSIS
    conffiles: You cannot use both, `myconf.ini` and
               `myconf.ini-template` in the same recipe.
    While:
      Installing.
      Getting section conffiles.
      Initializing part conffiles.
    Error: Duplicate file content definition


Template files must exist
-------------------------

This is obvious. If we name a not existing template file path, this
won't work::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = conffiles
    ...
    ... [conffiles]
    ... recipe = z3c.recipe.textfile
    ... myconf.ini-template = not_existing_template
    ... """)

    >>> print system(buildout) # doctest:+ELLIPSIS
    conffiles: No such template file: not_existing_template
    While:
      Installing.
      Getting section conffiles.
      Initializing part conffiles.
    Error: No such template file: not_existing_template


    >>> # ls('.')
    >>> cat('.installed.cfg')

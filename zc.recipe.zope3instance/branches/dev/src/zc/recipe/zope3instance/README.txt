Zope 3 Instance Recipe
======================

The zc.recipe.zope3instance recipe creates a Zope 3 instance.  A Zope
3 instance is a collection of scripts and configure that define a Zope
server process.

Let's start with a minimal example. We have a sample buildout.  Let's
write a buildout.cfg file that defines a zope instance:

    >>> cd(sample_buildout)
    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = instance
    ...
    ... [zope3]
    ... location = %(zope3_installation)s
    ...
    ... [mydata]
    ... zconfig = 
    ...     <zodb>
    ...        <filestorage>
    ...           path /foo/baz/Data.fs
    ...        </filestorage>
    ...     </zodb>
    ...
    ... [instance]
    ... database = mydata
    ... user = jim:SHA1:40bd001563085fc35165329ea1ff5c5ecbdbbeef
    ...
    ... """ 
    ... % dict(zope3_installation=sample_zope3))

The Zope3 instance recipe needs to be told the location of a Zope 3
installation.   This can be done in two ways:

1. Use a zope3checkout recipe to install Zope 3 from subversion, or

2. Create a section with an option that provides the location of a
   Zope 3 installation.


We provided a zope3 section containing the location of an existing
Zope3 installation.

We also provided a section that provided a zconfig option containing a
ZConfig definition for a database.  We provided it by hand, but one
would normally provide it using a part that used a database recipe,
such as zc.recipe.filestorage or zc.recipe.clientstorage recipe.

Let's run the buildout:

    >>> print system(join('bin', 'buildout')),
xs
We'll get a directory created in the buildout parts directory
containing configuration files and some directories to contain og
files, pid files, and so on.

    >>> ls(join('parts', 'instance'))


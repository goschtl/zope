Zope 3 Instance Recipe
======================

Credits
-------

The gocept.zope3instance recipe was derived from a development version of Jim
Fulton's original zc.recipe.zope3instance recipe.

Usage
-----

This recipe creates a Zope 3 instance.  A Zope 3 instance is a collection of
scripts and configuration that define a Zope server process.  This recipe is
likely to evolve quite a bit as our knowledge of how to deploy applications
with eggs evolves. For example, we now need to know the location of a Zope 3
installation, however, in the future, we may be able to express our dependence
on Zope3 soley via eggs.

Note that, currently, this recipe is fairly unix-centric.  Windows
support will be added in the future.

The zope3 instance recipe takes a number of options:

eggs
    Specify one or more distribution requirements, on separate lines,
    for software to be included in the Zope instance.

zope3
    The name of a section defining a Zope3 installation location (as a
    location option).  This can be either a checkout or a release
    installtion. (Unfortunately, we have to do some introspection to
    determine whether a checkout or release installation is
    provided.)  Hopefully, this option will be unnecessary in the
    future and we'll use egg depedencies to define the Zope software
    used. 

database
    The names of one or more sections defining databases to be used.
    These sections must contain zconfig options giving configurations
    for individual databases.

address
    One or more addresses to listed for HTTP connections on.  Each
    address of of the form "host:port" or just "port".

user
    A global management user of the form:
    user:encyption:encrypted-password.  

zcml 
    Specifications for one or more zcml files to be loaded.

options
    Top-level ZConfig options to be used for the instance.

In addition, the find-links, index, python, interpreter, and
extra-paths options of the zc.recipe.egg recipe are honored.

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
    ... recipe = gocept.zope3instance
    ... database = mydata
    ... user = jim:SHA1:40bd001563085fc35165329ea1ff5c5ecbdbbeef
    ...
    ... """ 
    ... % dict(zope3_installation=sample_zope3))

The Zope3 instance recipe needs to be told the location of a Zope 3
installation.   This can be done in two ways:

1. Use a zope3checkout recipe to install Zope 3 from subversion, 

2. Use the configure-make-make-install recipe to install a Zope
   release, or

3. Create a section with an option that provides the location of a
   Zope 3 installation.


We provided a zope3 section containing the location of an existing
Zope3 installation.

We also provided a section that provided a zconfig option containing a
ZConfig definition for a database.  We provided it by hand, but one
would normally provide it using a part that used a database recipe,
such as zc.recipe.filestorage or zc.recipe.clientstorage recipe.

Let's run the buildout:

    >>> print system(join('bin', 'buildout')),

We'll get a directory created in the buildout parts directory
containing configuration files and some directories to contain og
files, pid files, and so on.

    >>> ls(join('parts', 'instance'))


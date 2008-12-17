Using the deployment recipe is pretty simple. Jusr specify a
deployment name, specified via the part name, and a deployment user.

Let's add a deployment to a sample buildout:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = foo
    ...
    ... [foo]
    ... prefix = %s
    ... recipe = zc.recipe.deployment
    ... user = %s
    ... etc-user = %s
    ... ''' % (sample_buildout, user, user))

    >>> print system(join('bin', 'buildout')),
    Installing foo.
    zc.recipe.deployment: 
        Creating 'PREFIX/etc/foo',
        mode 755, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Creating 'PREFIX/var/log/foo',
        mode 755, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Creating 'PREFIX/var/run/foo',
        mode 750, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Creating 'PREFIX/etc/cron.d',
        mode 755, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Creating 'PREFIX/etc/init.d',
        mode 755, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Creating 'PREFIX/etc/logrotate.d',
        mode 755, user 'USER', group 'USER'


Note that we are providing a prefix and an etc-user here.  These options
default to '/' and 'root', respectively.

Now we can see that directories named foo in PREFIX/etc, PREFIX/var/log and
PREFIX/var/run have been created:

    >>> import os
    >>> print ls(os.path.join(sample_buildout, 'etc/foo'))
    drwxr-xr-x USER USER PREFIX/etc/foo

    >>> print ls(os.path.join(sample_buildout, 'var/log/foo')) 
    drwxr-xr-x USER USER PREFIX/var/log/foo

    >>> print ls(os.path.join(sample_buildout, 'var/run/foo'))
    drwxr-x--- USER USER PREFIX/var/run/foo

By looking at .installed.cfg, we can see the options available for use
by other recipes:

    >>> cat('.installed.cfg') # doctest: +ELLIPSIS
    [buildout]
    ...
    [foo]
    __buildout_installed__ = 
    ...
    crontab-directory = PREFIX/etc/cron.d
    etc-directory = PREFIX/etc/foo
    etc-user = USER
    log-directory = PREFIX/var/log/foo
    logrotate-directory = PREFIX/etc/logrotate.d
    name = foo
    prefix = PREFIX
    rc-directory = PREFIX/etc/init.d
    recipe = zc.recipe.deployment
    run-directory = PREFIX/var/run/foo
    user = USER

If we uninstall, then the directories are removed.

    >>> print system(join('bin', 'buildout')+' buildout:parts='),
    Uninstalling foo.
    Running uninstall recipe.
    zc.recipe.deployment: Removing 'PREFIX/etc/foo'
    zc.recipe.deployment: Removing 'PREFIX/etc/cron.d'.
    zc.recipe.deployment: Removing 'PREFIX/etc/init.d'.
    zc.recipe.deployment: Removing 'PREFIX/etc/logrotate.d'.
    zc.recipe.deployment: Removing 'PREFIX/var/log/foo'.
    zc.recipe.deployment: Removing 'PREFIX/var/run/foo'.

    >>> import os
    >>> os.path.exists(os.path.join(sample_buildout, 'etc/foo'))
    False
    >>> os.path.exists(os.path.join(sample_buildout, 'var/log/foo'))
    False
    >>> os.path.exists(os.path.join(sample_buildout, 'var/run/foo'))
    False

The log and run directories are only removed if they are empty.
To see that, we'll put a file in each of the directories created:

    >>> print system(join('bin', 'buildout')), # doctest: +ELLIPSIS
    Installing foo.
    zc.recipe.deployment: 
        Creating 'PREFIX/etc/foo',
        mode 755, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Creating 'PREFIX/var/log/foo',
        mode 755, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Creating 'PREFIX/var/run/foo',
        mode 750, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Creating 'PREFIX/etc/cron.d',
        mode 755, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Creating 'PREFIX/etc/init.d',
        mode 755, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Creating 'PREFIX/etc/logrotate.d',
        mode 755, user 'USER', group 'USER'

    >>> write(os.path.join(sample_buildout, 'etc/foo/x'), '')
    >>> write(os.path.join(sample_buildout, 'var/log/foo/x'), '')
    >>> write(os.path.join(sample_buildout, 'var/run/foo/x'), '')

And then uninstall:

    >>> print system(join('bin', 'buildout')+' buildout:parts='),
    Uninstalling foo.
    Running uninstall recipe.
    zc.recipe.deployment: Removing 'PREFIX/etc/foo'
    zc.recipe.deployment: Removing 'PREFIX/etc/cron.d'.
    zc.recipe.deployment: Removing 'PREFIX/etc/init.d'.
    zc.recipe.deployment: Removing 'PREFIX/etc/logrotate.d'.
    zc.recipe.deployment: Can't remove non-empty directory 'PREFIX/var/log/foo'.
    zc.recipe.deployment: Can't remove non-empty directory 'PREFIX/var/run/foo'.

    >>> os.path.exists(os.path.join(sample_buildout, 'etc/foo'))
    False

    >>> print ls(os.path.join(sample_buildout, 'var/log/foo'))
    drwxr-xr-x USER USER PREFIX/var/log/foo

    >>> print ls(os.path.join(sample_buildout, 'var/run/foo'))
    drwxr-x--- USER USER PREFIX/var/run/foo

Here we see that the var and run directories are kept. The etc
directory is discarded because only buildout recipes should write to
it and all of its data are expendible.

If we reinstall, remove the files, and uninstall, then the directories
are removed:

    >>> print system(join('bin', 'buildout')),
    Installing foo.
    zc.recipe.deployment: 
        Creating 'PREFIX/etc/foo',
        mode 755, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Updating 'PREFIX/var/log/foo',
        mode 755, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Updating 'PREFIX/var/run/foo',
        mode 750, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Creating 'PREFIX/etc/cron.d',
        mode 755, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Creating 'PREFIX/etc/init.d',
        mode 755, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Creating 'PREFIX/etc/logrotate.d',
        mode 755, user 'USER', group 'USER'

    >>> os.remove(os.path.join(sample_buildout, 'var/log/foo/x'))
    >>> os.remove(os.path.join(sample_buildout, 'var/run/foo/x'))

    >>> print system(join('bin', 'buildout')+' buildout:parts='),
    Uninstalling foo.
    Running uninstall recipe.
    zc.recipe.deployment: Removing 'PREFIX/etc/foo'
    zc.recipe.deployment: Removing 'PREFIX/etc/cron.d'.
    zc.recipe.deployment: Removing 'PREFIX/etc/init.d'.
    zc.recipe.deployment: Removing 'PREFIX/etc/logrotate.d'.
    zc.recipe.deployment: Removing 'PREFIX/var/log/foo'.
    zc.recipe.deployment: Removing 'PREFIX/var/run/foo'.

    >>> os.path.exists('' + os.path.join(sample_buildout, 'PREFIX/etc/foo'))
    False
    >>> os.path.exists('' + os.path.join(sample_buildout, 'PREFIX/var/log/foo'))
    False
    >>> os.path.exists('' + os.path.join(sample_buildout, 'PREFIX/var/run/foo'))
    False

Deployment Name
===============

The deployment name is used for naming generated files and directories.
The deployment name defaults to the section name, but the deployment
name can be specified explicitly:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = foo
    ...
    ... [foo]
    ... recipe = zc.recipe.deployment
    ... prefix = %s
    ... name = bar
    ... user = %s
    ... etc-user = %s
    ... ''' % (sample_buildout, user, user))

    >>> print system(join('bin', 'buildout')),
    Installing foo.
    zc.recipe.deployment: 
        Creating 'PREFIX/etc/bar',
        mode 755, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Creating 'PREFIX/var/log/bar',
        mode 755, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Creating 'PREFIX/var/run/bar',
        mode 750, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Creating 'PREFIX/etc/cron.d',
        mode 755, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Creating 'PREFIX/etc/init.d',
        mode 755, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Creating 'PREFIX/etc/logrotate.d',
        mode 755, user 'USER', group 'USER'


    >>> print ls(os.path.join(sample_buildout, 'etc/bar'))
    drwxr-xr-x USER USER PREFIX/etc/bar

    >>> print ls(os.path.join(sample_buildout, 'var/log/bar'))
    drwxr-xr-x USER USER PREFIX/var/log/bar

    >>> print ls(os.path.join(sample_buildout, 'var/run/bar'))
    drwxr-x--- USER USER PREFIX/var/run/bar

    >>> cat('.installed.cfg') # doctest: +ELLIPSIS
    [buildout]
    installed_develop_eggs = 
    parts = foo
    <BLANKLINE>
    [foo]
    __buildout_installed__ = 
    ...
    crontab-directory = PREFIX/etc/cron.d
    etc-directory = PREFIX/etc/bar
    etc-user = USER
    log-directory = PREFIX/var/log/bar
    logrotate-directory = PREFIX/etc/logrotate.d
    name = bar
    prefix = PREFIX
    rc-directory = PREFIX/etc/init.d
    recipe = zc.recipe.deployment
    run-directory = PREFIX/var/run/bar
    user = USER

Note (here and earlier) that the options include the name option,
which defaults to the part name.  Other parts that use the deployment
name should use the name option rather than the part name.

Configuration files
===================

Normally, configuration files are created by specialized recipes.
Sometimes, it's useful to specify configuration files in a buildout
configuration file.  The zc.recipe.deployment:configuration recipe can be
used to do that.

Let's add a configuration file to our buildout:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = foo x.cfg
    ...
    ... [foo]
    ... recipe = zc.recipe.deployment
    ... prefix = %s
    ... user = %s
    ... etc-user = %s
    ...
    ... [x.cfg]
    ... recipe = zc.recipe.deployment:configuration
    ... text = xxx
    ...        yyy
    ...        zzz
    ... ''' % (sample_buildout, user, user))

    >>> print system(join('bin', 'buildout')),
    Uninstalling foo.
    Running uninstall recipe.
    zc.recipe.deployment: Removing 'PREFIX/etc/bar'
    zc.recipe.deployment: Removing 'PREFIX/etc/cron.d'.
    zc.recipe.deployment: Removing 'PREFIX/etc/init.d'.
    zc.recipe.deployment: Removing 'PREFIX/etc/logrotate.d'.
    zc.recipe.deployment: Removing 'PREFIX/var/log/bar'.
    zc.recipe.deployment: Removing 'PREFIX/var/run/bar'.
    Installing foo.
    zc.recipe.deployment: 
        Creating 'PREFIX/etc/foo',
        mode 755, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Creating 'PREFIX/var/log/foo',
        mode 755, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Creating 'PREFIX/var/run/foo',
        mode 750, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Creating 'PREFIX/etc/cron.d',
        mode 755, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Creating 'PREFIX/etc/init.d',
        mode 755, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Creating 'PREFIX/etc/logrotate.d',
        mode 755, user 'USER', group 'USER'
    Installing x.cfg.

By default, the configuration is installed as a part:

    >>> cat('parts', 'x.cfg')
    xxx
    yyy
    zzz

If a deployment is specified, then the file is placed in the
deployment etc directory:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = foo x.cfg
    ...
    ... [foo]
    ... recipe = zc.recipe.deployment
    ... prefix = %s
    ... user = %s
    ... etc-user = %s
    ...
    ... [x.cfg]
    ... recipe = zc.recipe.deployment:configuration
    ... text = xxx
    ...        yyy
    ...        zzz
    ... deployment = foo
    ... ''' % (sample_buildout, user, user))

    >>> print system(join('bin', 'buildout')),
    Uninstalling x.cfg.
    Updating foo.
    Installing x.cfg.

    >>> os.path.exists(join('parts', 'x.cfg'))
    False

    >>> cat(os.path.join(sample_buildout, 'etc/foo/x.cfg'))
    xxx
    yyy
    zzz

We can read data from a file rather than specifying in the
configuration:

    >>> write('x.in', '1\n2\n3\n')

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = foo x.cfg
    ...
    ... [foo]
    ... recipe = zc.recipe.deployment
    ... prefix = %s
    ... user = %s
    ... etc-user = %s
    ...
    ... [x.cfg]
    ... recipe = zc.recipe.deployment:configuration
    ... file = x.in
    ... deployment = foo
    ... ''' % (sample_buildout, user, user))

    >>> print system(join('bin', 'buildout')),
    Uninstalling x.cfg.
    Updating foo.
    Installing x.cfg.

    >>> cat(os.path.join(sample_buildout, 'etc/foo/x.cfg'))
    1
    2
    3

The recipe sets a location option that can be used by other recipes:

    >>> cat('.installed.cfg') # doctest: +ELLIPSIS
    [buildout]
    ...
    [x.cfg]
    ...
    location = PREFIX/etc/foo/x.cfg
    ...

Cron support
============

The crontab recipe provides support for creating crontab files.  It
uses a times option to specify times to run the command and a command
option containing the command.

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = foo cron
    ...
    ... [foo]
    ... recipe = zc.recipe.deployment
    ... prefix = %s
    ... user = %s
    ... etc-user = %s
    ...
    ... [cron]
    ... recipe = zc.recipe.deployment:crontab
    ... times = 30 23 * * *
    ... command = echo hello world!
    ... deployment = foo
    ... ''' % (sample_buildout, user, user))

    >>> print system(join('bin', 'buildout')),
    Uninstalling x.cfg.
    Updating foo.
    Installing cron.

This example creates PREFIX/etc/cron.d/foo-cron

    >>> open(os.path.join(sample_buildout, 'etc/cron.d/foo-cron')).read()
    '30 23 * * *\tUSER\techo hello world!\n'

.. make sure cron recipe honors deployment name option:


    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = foo cron
    ...
    ... [foo]
    ... recipe = zc.recipe.deployment
    ... prefix = %s
    ... name = bar
    ... user = %s
    ... etc-user = %s
    ...
    ... [cron]
    ... recipe = zc.recipe.deployment:crontab
    ... times = 30 23 * * *
    ... command = echo hello world!
    ... deployment = foo
    ... ''' % (sample_buildout, user, user))

    >>> print system(join('bin', 'buildout')),
    Uninstalling cron.
    Uninstalling foo.
    Running uninstall recipe.
    zc.recipe.deployment: Removing 'PREFIX/etc/foo'
    zc.recipe.deployment: Removing 'PREFIX/etc/cron.d'.
    zc.recipe.deployment: Removing 'PREFIX/etc/init.d'.
    zc.recipe.deployment: Removing 'PREFIX/etc/logrotate.d'.
    zc.recipe.deployment: Removing 'PREFIX/var/log/foo'.
    zc.recipe.deployment: Removing 'PREFIX/var/run/foo'.
    Installing foo.
    zc.recipe.deployment: 
        Creating 'PREFIX/etc/bar',
        mode 755, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Creating 'PREFIX/var/log/bar',
        mode 755, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Creating 'PREFIX/var/run/bar',
        mode 750, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Creating 'PREFIX/etc/cron.d',
        mode 755, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Creating 'PREFIX/etc/init.d',
        mode 755, user 'USER', group 'USER'
    zc.recipe.deployment: 
        Creating 'PREFIX/etc/logrotate.d',
        mode 755, user 'USER', group 'USER'
    Installing cron.

    >>> open(os.path.join(sample_buildout, 'etc/cron.d/bar-cron')).read()
    '30 23 * * *\tUSER\techo hello world!\n'

.. cleanup

    >>> print system(join('bin', 'buildout')+' buildout:parts='),
    Uninstalling cron.
    Uninstalling foo.
    Running uninstall recipe.
    zc.recipe.deployment: Removing 'PREFIX/etc/bar'
    zc.recipe.deployment: Removing 'PREFIX/etc/cron.d'.
    zc.recipe.deployment: Removing 'PREFIX/etc/init.d'.
    zc.recipe.deployment: Removing 'PREFIX/etc/logrotate.d'.
    zc.recipe.deployment: Removing 'PREFIX/var/log/bar'.
    zc.recipe.deployment: Removing 'PREFIX/var/run/bar'.

    >>> os.path.exists(os.path.join(sample_buildout, 'etc/cron.d/bar-cron'))
    False
    

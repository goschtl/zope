Using the deployment recipe is pretty simple. Jusr specify a
deployment name, specified via the part name, and a deployment user.

Let's add a deployment to a sample buildout:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = foo
    ...
    ... [foo]
    ... recipe = zc.recipe.deployment
    ... user = jim
    ... ''')

    >>> print system(join('bin', 'buildout')),
    Installing foo.
    zc.recipe.deployment: 
        Creating '/etc/foo',
        mode 755, user 'root', group 'root'
    zc.recipe.deployment: 
        Creating '/var/log/foo',
        mode 755, user 'jim', group 'jim'
    zc.recipe.deployment: 
        Creating '/var/run/foo',
        mode 750, user 'jim', group 'jim'


(Note that we have to be running as root and must have a user jim for
this to work.)

Now we can see that directories named foo in /etc, /var/log and
/var/run have been created:

    >>> print system('ls -ld /etc/foo'), 
    drwxr-xr-x 2 root root 4096 2007-02-06 09:50 /etc/foo

    >>> print system('ls -ld /var/log/foo'), 
    drwxr-xr-x 2 jim jim 4096 2007-02-06 09:50 /var/log/foo

    >>> print system('ls -ld /var/run/foo'), 
    drwxr-x--- 2 jim jim 40 2007-02-06 09:50 /var/run/foo
    
By looking at .installed.cfg, we can see the options available for use
by other recipes:

    >>> cat('.installed.cfg') # doctest: +ELLIPSIS
    [buildout]
    ...
    [foo]
    __buildout_installed__ = 
    ...
    crontab-directory = /etc/cron.d
    etc-directory = /etc/foo
    log-directory = /var/log/foo
    logrotate-directory = /etc/logrotate.d
    name = foo
    rc-directory = /etc/init.d
    recipe = zc.recipe.deployment
    run-directory = /var/run/foo
    user = jim

If we ininstall, then the directories are removed.

    >>> print system(join('bin', 'buildout')+' buildout:parts='),
    Uninstalling foo.
    Running uninstall recipe.
    zc.recipe.deployment: Removing '/etc/foo'
    zc.recipe.deployment: Removing '/var/log/foo'.
    zc.recipe.deployment: Removing '/var/run/foo'.

    >>> import os
    >>> os.path.exists('/etc/foo')
    False
    >>> os.path.exists('/var/log/foo')
    False
    >>> os.path.exists('/var/run/foo')
    False

The log and run directories are only removed if they are empty.
To see that, we'll put a file in each of the directories created:

    >>> print system(join('bin', 'buildout')), # doctest: +ELLIPSIS
    Installing foo.
    ...

    >>> write('/etc/foo/x', '')
    >>> write('/var/log/foo/x', '')
    >>> write('/var/run/foo/x', '')

And then uninstall:

    >>> print system(join('bin', 'buildout')+' buildout:parts='),
    Uninstalling foo.
    Running uninstall recipe.
    zc.recipe.deployment: Removing '/etc/foo'
    zc.recipe.deployment: Can't remove non-empty directory '/var/log/foo'.
    zc.recipe.deployment: Can't remove non-empty directory '/var/run/foo'.

    >>> os.path.exists('/etc/foo')
    False

    >>> print system('ls -ld /var/log/foo'), 
    drwxr-xr-x 2 jim jim 4096 2007-02-06 09:50 /var/log/foo

    >>> print system('ls -ld /var/run/foo'), 
    drwxr-x--- 2 jim jim 40 2007-02-06 09:50 /var/run/foo

Here we see that the var and run directories are kept. The etc
directory is discarded because only buildout recipes should write to
it and all of it's data are expendible.

If we reinstall, remove the files, and uninstall, then the directories
are removed:

    >>> print system(join('bin', 'buildout')),
    Installing foo.
    zc.recipe.deployment: 
        Creating '/etc/foo',
        mode 755, user 'root', group 'root'
    zc.recipe.deployment: 
        Updating '/var/log/foo',
        mode 755, user 'jim', group 'jim'
    zc.recipe.deployment: 
        Updating '/var/run/foo',
        mode 750, user 'jim', group 'jim'

    >>> os.remove('/var/log/foo/x')
    >>> os.remove('/var/run/foo/x')

    >>> print system(join('bin', 'buildout')+' buildout:parts='),
    Uninstalling foo.
    Running uninstall recipe.
    zc.recipe.deployment: Removing '/etc/foo'
    zc.recipe.deployment: Removing '/var/log/foo'.
    zc.recipe.deployment: Removing '/var/run/foo'.

    >>> os.path.exists('/etc/foo')
    False
    >>> os.path.exists('/var/log/foo')
    False
    >>> os.path.exists('/var/run/foo')
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
    ... name = bar
    ... user = jim
    ... ''')

    >>> print system(join('bin', 'buildout')),
    Installing foo.
    zc.recipe.deployment: 
        Creating '/etc/bar',
        mode 755, user 'root', group 'root'
    zc.recipe.deployment: 
        Creating '/var/log/bar',
        mode 755, user 'jim', group 'jim'
    zc.recipe.deployment: 
        Creating '/var/run/bar',
        mode 750, user 'jim', group 'jim'

    >>> print system('ls -ld /etc/bar'), 
    drwxr-xr-x 2 root root 4096 2007-02-06 09:50 /etc/bar

    >>> print system('ls -ld /var/log/bar'), 
    drwxr-xr-x 2 jim jim 4096 2007-02-06 09:50 /var/log/bar

    >>> print system('ls -ld /var/run/bar'), 
    drwxr-x--- 2 jim jim 40 2007-02-06 09:50 /var/run/bar

    >>> cat('.installed.cfg') # doctest: +ELLIPSIS
    [buildout]
    installed_develop_eggs = 
    parts = foo
    <BLANKLINE>
    [foo]
    __buildout_installed__ = 
    ...
    crontab-directory = /etc/cron.d
    etc-directory = /etc/bar
    log-directory = /var/log/bar
    logrotate-directory = /etc/logrotate.d
    name = bar
    rc-directory = /etc/init.d
    recipe = zc.recipe.deployment
    run-directory = /var/run/bar
    user = jim

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
    ... user = jim
    ...
    ... [x.cfg]
    ... recipe = zc.recipe.deployment:configuration
    ... text = xxx
    ...        yyy
    ...        zzz
    ... ''')

    >>> print system(join('bin', 'buildout')),
    Uninstalling foo.
    Running uninstall recipe.
    zc.recipe.deployment: Removing '/etc/bar'
    zc.recipe.deployment: Removing '/var/log/bar'.
    zc.recipe.deployment: Removing '/var/run/bar'.
    Installing foo.
    zc.recipe.deployment: 
        Creating '/etc/foo',
        mode 755, user 'root', group 'root'
    zc.recipe.deployment: 
        Creating '/var/log/foo',
        mode 755, user 'jim', group 'jim'
    zc.recipe.deployment: 
        Creating '/var/run/foo',
        mode 750, user 'jim', group 'jim'
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
    ... user = jim
    ...
    ... [x.cfg]
    ... recipe = zc.recipe.deployment:configuration
    ... text = xxx
    ...        yyy
    ...        zzz
    ... deployment = foo
    ... ''')

    >>> print system(join('bin', 'buildout')),
    Uninstalling x.cfg.
    Updating foo.
    Installing x.cfg.

    >>> os.path.exists(join('parts', 'x.cfg'))
    False

    >>> cat('/etc/foo/x.cfg')
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
    ... user = jim
    ...
    ... [x.cfg]
    ... recipe = zc.recipe.deployment:configuration
    ... file = x.in
    ... deployment = foo
    ... ''')

    >>> print system(join('bin', 'buildout')),
    Uninstalling x.cfg.
    Updating foo.
    Installing x.cfg.

    >>> cat('/etc/foo/x.cfg')
    1
    2
    3

The recipe sets a location option that can be used by other recipes:

    >>> cat('.installed.cfg') # doctest: +ELLIPSIS
    [buildout]
    ...
    [x.cfg]
    ...
    location = /etc/foo/x.cfg
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
    ... user = jim
    ...
    ... [cron]
    ... recipe = zc.recipe.deployment:crontab
    ... times = 30 23 * * *
    ... command = echo hello world!
    ... deployment = foo
    ... ''')

    >>> print system(join('bin', 'buildout')),
    Uninstalling x.cfg.
    Updating foo.
    Installing cron.

This example creates /etc/cron.d/foo-cron

    >>> open('/etc/cron.d/foo-cron').read()
    '30 23 * * *\tjim\techo hello world!\n'

.. make sure cron recipe honors deployment name option:


    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = foo cron
    ...
    ... [foo]
    ... recipe = zc.recipe.deployment
    ... name = bar
    ... user = jim
    ...
    ... [cron]
    ... recipe = zc.recipe.deployment:crontab
    ... times = 30 23 * * *
    ... command = echo hello world!
    ... deployment = foo
    ... ''')

    >>> print system(join('bin', 'buildout')),
    Uninstalling cron.
    Uninstalling foo.
    Running uninstall recipe.
    zc.recipe.deployment: Removing '/etc/foo'
    zc.recipe.deployment: Removing '/var/log/foo'.
    zc.recipe.deployment: Removing '/var/run/foo'.
    Installing foo.
    zc.recipe.deployment: 
        Creating '/etc/bar',
        mode 755, user 'root', group 'root'
    zc.recipe.deployment: 
        Creating '/var/log/bar',
        mode 755, user 'jim', group 'jim'
    zc.recipe.deployment: 
        Creating '/var/run/bar',
        mode 750, user 'jim', group 'jim'
    Installing cron.

    >>> open('/etc/cron.d/bar-cron').read()
    '30 23 * * *\tjim\techo hello world!\n'


.. cleanup

    >>> print system(join('bin', 'buildout')+' buildout:parts='),
    Uninstalling cron.
    Uninstalling foo.
    Running uninstall recipe.
    zc.recipe.deployment: Removing '/etc/bar'
    zc.recipe.deployment: Removing '/var/log/bar'.
    zc.recipe.deployment: Removing '/var/run/bar'.

    >>> os.path.exists('/etc/cron.d/bar-cron')
    False
    

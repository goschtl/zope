Using the deployment recipe is pretty simple. Jusr specify a
deployment name, specified via the part name, and a deployment user.

Let's add a deployment to a sample buildout:

    >>> import os, pwd, tempfile
    >>> runninguser = pwd.getpwuid(os.getuid())[0]
    >>> tdir = tempfile.mkdtemp()
    >>> os.mkdir(os.path.join(tdir, 'etc'))
    >>> os.mkdir(os.path.join(tdir, 'log'))
    >>> os.mkdir(os.path.join(tdir, 'run'))

    >>> fixup = lambda x: x.replace(runninguser, 'jim').replace(tdir, '_tdir_')

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = foo
    ...
    ... [foo]
    ... recipe = zc.recipe.deployment
    ... name = foo
    ... user = %(user)s
    ... etc-directory = %(tdir)s/etc
    ... log-directory = %(tdir)s/log
    ... run-directory = %(tdir)s/run
    ... ''' % ({ 'user':runninguser, 'tdir':tdir}))

    >>> print fixup(system(join('bin', 'buildout'))), # doctest: +NORMALIZE_WHITESPACE
    Installing foo.
    zc.recipe.deployment:
        Creating '_tdir_/etc/foo',
        mode 755, user 'jim', group 'jim'
    zc.recipe.deployment:
        Creating '_tdir_/log/foo',
        mode 755, user 'jim', group 'jim'
    zc.recipe.deployment:
        Creating '_tdir_/run/foo',
        mode 750, user 'jim', group 'jim'

Now we can see that directories named foo in /etc, /var/log and
/var/run have been created:

    >>> print fixup(system('ls -ld %s/etc/foo' % (tdir))), #doctest: +ELLIPSIS
    drwxr-xr-x ... _tdir_/etc/foo

    >>> print fixup(system('ls -ld %s/log/foo' % (tdir))), #doctest: +ELLIPSIS
    drwxr-xr-x ... _tdir_/log/foo

    >>> print fixup(system('ls -ld %s/run/foo' % (tdir))), #doctest: +ELLIPSIS
    drwxr-x--- ... _tdir_/run/foo

By looking at .installed.cfg, we can see the options available for use
by other recipes:

    >>> print fixup(file('.installed.cfg').read()) # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    [buildout]
    ...
    [foo]
    __buildout_installed__ =
    ...
    crontab-directory = /etc/cron.d
    etc-directory = _tdir_/etc/foo
    log-directory = _tdir_/log/foo
    logrotate-directory = /etc/logrotate.d
    name = foo
    rc-directory = /etc/init.d
    recipe = zc.recipe.deployment
    run-directory = _tdir_/run/foo
    user = jim

If we ininstall, then the directories are removed.

    >>> print fixup(system(os.path.join('bin', 'buildout')+' buildout:parts=')),
    Uninstalling foo.
    Running uninstall recipe.
    zc.recipe.deployment: Removing '_tdir_/etc/foo'
    zc.recipe.deployment: Removing '_tdir_/log/foo'.
    zc.recipe.deployment: Removing '_tdir_/run/foo'.

    >>> import os
    >>> os.path.exists(os.path.join(tdir, '/etc/foo'))
    False
    >>> os.path.exists(os.path.join(tdir, '/log/foo'))
    False
    >>> os.path.exists(os.path.join(tdir, '/run/foo'))
    False

The log and run directories are only removed if they are empty.
To see that, we'll put a file in each of the directories created:

    >>> print system(join('bin', 'buildout')), # doctest: +ELLIPSIS
    Installing foo.
    ...

    >>> write(os.path.join(tdir, 'etc/foo/x'), '')
    >>> write(os.path.join(tdir, 'log/foo/x'), '')
    >>> write(os.path.join(tdir, 'run/foo/x'), '')

And then uninstall:

    >>> print fixup(system(join('bin', 'buildout')+' buildout:parts=')),
    Uninstalling foo.
    Running uninstall recipe.
    zc.recipe.deployment: Removing '_tdir_/etc/foo'
    zc.recipe.deployment: Can't remove non-empty directory '_tdir_/log/foo'.
    zc.recipe.deployment: Can't remove non-empty directory '_tdir_/run/foo'.

    >>> os.path.exists(os.path.join(tdir, '/etc/foo'))
    False

    >>> print fixup(system('ls -ld %s' % (os.path.join(tdir, 'log/foo')))),  # doctest: +ELLIPSIS
    drwxr-xr-x ... _tdir_/log/foo

    >>> print fixup(system('ls -ld %s' % (os.path.join(tdir, 'run/foo')))),  # doctest: +ELLIPSIS
    drwxr-x--- ... _tdir_/run/foo

Here we see that the var and run directories are kept. The etc
directory is discarded because only buildout recipes should write to
it and all of it's data are expendible.

If we reinstall, remove the files, and uninstall, then the directories
are removed:

    >>> print fixup(system(os.path.join('bin', 'buildout'))), # doctest: +NORMALIZE_WHITESPACE
    Installing foo.
    zc.recipe.deployment:
        Creating '_tdir_/etc/foo',
        mode 755, user 'jim', group 'jim'
    zc.recipe.deployment:
        Updating '_tdir_/log/foo',
        mode 755, user 'jim', group 'jim'
    zc.recipe.deployment:
        Updating '_tdir_/run/foo',
        mode 750, user 'jim', group 'jim'

    >>> os.remove(os.path.join(tdir, 'log/foo/x'))
    >>> os.remove(os.path.join(tdir, 'run/foo/x'))

    >>> print fixup(system(join('bin', 'buildout')+' buildout:parts=')),
    Uninstalling foo.
    Running uninstall recipe.
    zc.recipe.deployment: Removing '_tdir_/etc/foo'
    zc.recipe.deployment: Removing '_tdir_/log/foo'.
    zc.recipe.deployment: Removing '_tdir_/run/foo'.

    >>> os.path.exists(os.path.join(tdir, '/etc/foo'))
    False
    >>> os.path.exists(os.path.join(tdir, '/log/foo'))
    False
    >>> os.path.exists(os.path.join(tdir, '/run/foo'))
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
    ... user = %(user)s
    ... etc-directory = %(tdir)s/etc
    ... log-directory = %(tdir)s/log
    ... run-directory = %(tdir)s/run
    ... ''' % ({ 'user':runninguser, 'tdir':tdir}))

    >>> print fixup(system(os.path.join('bin', 'buildout'))), #doctest: +NORMALIZE_WHITESPACE
    Installing foo.
    zc.recipe.deployment:
        Creating '_tdir_/etc/bar',
        mode 755, user 'jim', group 'jim'
    zc.recipe.deployment:
        Creating '_tdir_/log/bar',
        mode 755, user 'jim', group 'jim'
    zc.recipe.deployment:
        Creating '_tdir_/run/bar',
        mode 750, user 'jim', group 'jim'

    >>> print fixup(system('ls -ld %s/etc/bar' % (tdir))), #doctest: +ELLIPSIS
    drwxr-xr-x ... _tdir_/etc/bar

    >>> print fixup(system('ls -ld %s/log/bar' % (tdir))), #doctest: +ELLIPSIS
    drwxr-xr-x ... _tdir_/log/bar

    >>> print fixup(system('ls -ld %s/run/bar' % (tdir))), #doctest: +ELLIPSIS
    drwxr-x--- ... _tdir_/run/bar

    >>> print fixup(file('.installed.cfg').read()) # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    [buildout]
    installed_develop_eggs =
    parts = foo
    <BLANKLINE>
    [foo]
    __buildout_installed__ =
    ...
    crontab-directory = /etc/cron.d
    etc-directory = _tdir_/etc/bar
    log-directory = _tdir_/log/bar
    logrotate-directory = /etc/logrotate.d
    name = bar
    rc-directory = /etc/init.d
    recipe = zc.recipe.deployment
    run-directory = _tdir_/run/bar
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
    ... user = %(user)s
    ... etc-directory = %(tdir)s/etc
    ... log-directory = %(tdir)s/log
    ... run-directory = %(tdir)s/run
    ...
    ... [x.cfg]
    ... recipe = zc.recipe.deployment:configuration
    ... text = xxx
    ...        yyy
    ...        zzz
    ... ''' % ({ 'user':runninguser, 'tdir':tdir}))

    >>> print fixup(system(os.path.join('bin', 'buildout'))), # doctest: +NORMALIZE_WHITESPACE
    Uninstalling foo.
    Running uninstall recipe.
    zc.recipe.deployment: Removing '_tdir_/etc/bar'
    zc.recipe.deployment: Removing '_tdir_/log/bar'.
    zc.recipe.deployment: Removing '_tdir_/run/bar'.
    Installing foo.
    zc.recipe.deployment:
        Creating '_tdir_/etc/foo',
        mode 755, user 'jim', group 'jim'
    zc.recipe.deployment:
        Creating '_tdir_/log/foo',
        mode 755, user 'jim', group 'jim'
    zc.recipe.deployment:
        Creating '_tdir_/run/foo',
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
    ... user = %(user)s
    ... etc-directory = %(tdir)s/etc
    ... log-directory = %(tdir)s/log
    ... run-directory = %(tdir)s/run
    ...
    ... [x.cfg]
    ... recipe = zc.recipe.deployment:configuration
    ... text = xxx
    ...        yyy
    ...        zzz
    ... deployment = foo
    ... ''' % ({ 'user':runninguser, 'tdir':tdir}))

    >>> print system(os.path.join('bin', 'buildout')),
    Uninstalling x.cfg.
    Updating foo.
    Installing x.cfg.

    >>> os.path.exists(os.path.join('parts', 'x.cfg'))
    False

    >>> cat(tdir, 'etc/foo/x.cfg')
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
    ... user = %(user)s
    ... etc-directory = %(tdir)s/etc
    ... log-directory = %(tdir)s/log
    ... run-directory = %(tdir)s/run
    ...
    ... [x.cfg]
    ... recipe = zc.recipe.deployment:configuration
    ... file = x.in
    ... deployment = foo
    ... ''' % ({ 'user':runninguser, 'tdir':tdir}))

    >>> print system(join('bin', 'buildout')),
    Uninstalling x.cfg.
    Updating foo.
    Installing x.cfg.

    >>> cat(tdir, 'etc/foo/x.cfg')
    1
    2
    3

The recipe sets a location option that can be used by other recipes:

    >>> print fixup(file('.installed.cfg').read()) # doctest: +ELLIPSIS
    [buildout]
    ...
    [x.cfg]
    ...
    location = _tdir_/etc/foo/x.cfg
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
    ... user = %(user)s
    ... etc-directory = %(tdir)s/etc
    ... log-directory = %(tdir)s/log
    ... run-directory = %(tdir)s/run
    ... crontab-directory = %(tdir)s/etc
    ...
    ... [cron]
    ... recipe = zc.recipe.deployment:crontab
    ... times = 30 23 * * *
    ... command = echo hello world!
    ... deployment = foo
    ... ''' % ({ 'user':runninguser, 'tdir':tdir}))

    >>> print fixup(system(os.path.join('bin', 'buildout'))), # doctest: +ELLIPSIS
    Uninstalling x.cfg.
    Uninstalling foo.
    ...
    Installing foo.
    ...
    Installing cron.

This example creates _tdir_/etc/foo-cron

    >>> fixup(file(os.path.join(tdir,'etc/foo-cron'), 'r').read())
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
    ... user = %(user)s
    ... etc-directory = %(tdir)s/etc
    ... log-directory = %(tdir)s/log
    ... run-directory = %(tdir)s/run
    ... crontab-directory = %(tdir)s/etc
    ...
    ... [cron]
    ... recipe = zc.recipe.deployment:crontab
    ... times = 30 23 * * *
    ... command = echo hello world!
    ... deployment = foo
    ... ''' % ({ 'user':runninguser, 'tdir':tdir}))

    >>> print fixup(system(os.path.join('bin', 'buildout'))), # doctest: +NORMALIZE_WHITESPACE
    Uninstalling cron.
    Uninstalling foo.
    Running uninstall recipe.
    zc.recipe.deployment: Removing '_tdir_/etc/foo'
    zc.recipe.deployment: Removing '_tdir_/log/foo'.
    zc.recipe.deployment: Removing '_tdir_/run/foo'.
    Installing foo.
    zc.recipe.deployment:
        Creating '_tdir_/etc/bar',
        mode 755, user 'jim', group 'jim'
    zc.recipe.deployment:
        Creating '_tdir_/log/bar',
        mode 755, user 'jim', group 'jim'
    zc.recipe.deployment:
        Creating '_tdir_/run/bar',
        mode 750, user 'jim', group 'jim'
    Installing cron.

    >>> fixup(open(os.path.join(tdir, 'etc/bar-cron')).read())
    '30 23 * * *\tjim\techo hello world!\n'


.. cleanup

    >>> print fixup(system(join('bin', 'buildout')+' buildout:parts=')),
    Uninstalling cron.
    Uninstalling foo.
    Running uninstall recipe.
    zc.recipe.deployment: Removing '_tdir_/etc/bar'
    zc.recipe.deployment: Removing '_tdir_/log/bar'.
    zc.recipe.deployment: Removing '_tdir_/run/bar'.

    >>> os.path.exists(os.path.join(tdir, 'etc/bar-cron'))
    False

... and cleanup the tmpdir
    >>> import shutil
    >>> shutil.rmtree(tdir)

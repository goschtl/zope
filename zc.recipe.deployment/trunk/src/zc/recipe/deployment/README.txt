Using the deplyment recipe is pretty simple. Simply specify a
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
    buildout: Installing foo
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

    >>> cat('.installed.cfg')
    ... # doctest: +ELLIPSIS
    [buildout]
    ...
    [foo]
    __buildout_installed__ = 
    ...
    crontab-directory = /etc/cron.d
    etc-directory = /etc/foo
    log-directory = /var/log/foo
    rc-directory = /etc/init.d
    recipe = zc.recipe.deployment
    run-directory = /var/run/foo
    user = jim

If we ininstall, then the directories are removed.

    >>> print system(join('bin', 'buildout')+' buildout:parts='),
    buildout: Uninstalling foo
    buildout: Running uninstall recipe
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

The log and run directories are only removed if they are non-empty.
To see that, we'll put a file in each of the directories created:

    >>> print system(join('bin', 'buildout')), # doctest: +ELLIPSIS
    buildout: Installing foo
    ...

    >>> write('/etc/foo/x', '')
    >>> write('/var/log/foo/x', '')
    >>> write('/var/run/foo/x', '')

And then uninstall:

    >>> print system(join('bin', 'buildout')+' buildout:parts='),
    buildout: Uninstalling foo
    buildout: Running uninstall recipe
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
    buildout: Installing foo
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
    buildout: Uninstalling foo
    buildout: Running uninstall recipe
    zc.recipe.deployment: Removing '/etc/foo'
    zc.recipe.deployment: Removing '/var/log/foo'.
    zc.recipe.deployment: Removing '/var/run/foo'.

    >>> os.path.exists('/etc/foo')
    False
    >>> os.path.exists('/var/log/foo')
    False
    >>> os.path.exists('/var/run/foo')
    False

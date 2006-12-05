Create Red-Hat Linux (chkconfig) rc scripts
===========================================

The zc.recipes.rhrc recipe creates Red-Hat Linux (chkconfig) rc
scripts.   It can create individual rc scripts, as well as combined rc
scripts that start multiple applications.

The recipe has a parts option that takes the names of sections that
define run-script options, which contain one-line control scripts.  Let's
look at a simple example.

A simple example will, hopefully make this clearer. 

    >>> demo = tmpdir('demo')

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = zoperc
    ...
    ... [zoperc]
    ... recipe = zc.recipe.rhrc
    ... parts = zope
    ... dest = %(dest)s
    ...
    ... [zope]
    ... run-script = /opt/zope/bin/zopectl -C /etc/zope.conf
    ... """ % dict(dest=demo))

Normally the recipe writes scripts to /etc/init.d.  We can override
the destivation, which we've done here, using a demonstration
directory.  We specified a that it should get run-script source from
the zope section.  Here the zope section is simply a configuration
section with a run-script option set directly, but it could have been
a part with a run-script option computed from the recipe.

If we run the buildout:

    >>> print system('bin/buildout'),
    buildout: Installing zoperc

We'll get a zoperc script in our demo directory:

    >>> ls(demo)
    -  zoperc
    
    >>> cat(demo, 'zoperc')
    #!/bin/sh 
    <BLANKLINE>
    # This script is for adminstrator convenience.  It should
    # NOT be installed as a system startup script!
    <BLANKLINE>
    <BLANKLINE>
    case $1 in 
      stop)
    <BLANKLINE>
        /opt/zope/bin/zopectl -C /etc/zope.conf $*
    <BLANKLINE>
        ;;
      restart)
    <BLANKLINE>
        ${0} stop
        sleep 1
        ${0} start
    <BLANKLINE>
        ;;
      *) 
    <BLANKLINE>
        /opt/zope/bin/zopectl -C /etc/zope.conf $*
    <BLANKLINE>
        ;;
    esac
    <BLANKLINE>

There are a couple of things to note about the generated script:

- It uses $* to pass arguments, so arguments can't be quoted.  This is 
  OK because the arguments will be simple verbs like start and stop.

- It includes a comment saying that the script shouldn't be used as a
  system startup script.

For the script to be used for system startup, we need to specify
run-level information.  We can to that using the chkconfig option:

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = zoperc
    ...
    ... [zoperc]
    ... recipe = zc.recipe.rhrc
    ... parts = zope
    ... dest = %(dest)s
    ... chkconfig = 345 90 10
    ... chkconfigcommand = echo
    ...
    ... [zope]
    ... run-script = /opt/zope/bin/zopectl -C /etc/zope.conf
    ... """ % dict(dest=demo))

Here we included a chkconfig option saying that Zope should be started
at run levels 3, 4, and 5 and that it's start and stop ordered should
be 90 and 10.

For demonstration purposes, we don't *really* want to run chkconfig,
so we use the chkconfigcommand option to tell the recipe to run echo
instead.

    >>> print system('bin/buildout'),
    buildout: Uninstalling zoperc
    buildout: Running uninstall recipe
    buildout: Installing zoperc
    --add zoperc

Now the script contains a chkconfig comment:

    >>> cat(demo, 'zoperc')
    #!/bin/sh 
    <BLANKLINE>
    # the next line is for chkconfig
    # chkconfig: 345 90 10
    # description: please, please work
    <BLANKLINE>
    <BLANKLINE>
    case $1 in 
      stop)
    <BLANKLINE>
        /opt/zope/bin/zopectl -C /etc/zope.conf $* \
          </dev/null
    <BLANKLINE>
        ;;
      restart)
    <BLANKLINE>
        ${0} stop
        sleep 1
        ${0} start
    <BLANKLINE>
        ;;
      *) 
    <BLANKLINE>
        /opt/zope/bin/zopectl -C /etc/zope.conf $* \
          </dev/null
    <BLANKLINE>
        ;;
    esac
    <BLANKLINE>

We can specify a user that the script should be run as:

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = zoperc
    ...
    ... [zoperc]
    ... recipe = zc.recipe.rhrc
    ... parts = zope
    ... dest = %(dest)s
    ... chkconfig = 345 90 10
    ... chkconfigcommand = echo
    ... user = zope
    ...
    ... [zope]
    ... run-script = /opt/zope/bin/zopectl -C /etc/zope.conf
    ... """ % dict(dest=demo))

    >>> print system('bin/buildout'),
    buildout: Uninstalling zoperc
    buildout: Running uninstall recipe
    --del zoperc
    buildout: Installing zoperc
    --add zoperc

Note the --del output.  If we hadn't set the chkconfigcommand to echo,
then chkconfig --del would have been run on the zoperc script.

    >>> cat(demo, 'zoperc')
    #!/bin/sh 
    <BLANKLINE>
    # the next line is for chkconfig
    # chkconfig: 345 90 10
    # description: please, please work
    <BLANKLINE>
    <BLANKLINE>
    if [ $(whoami) != "root" ]; then
      echo "You must be root."
      exit 1
    fi
    <BLANKLINE>
    case $1 in 
      stop)
    <BLANKLINE>
        su zope -c \
          "/opt/zope/bin/zopectl -C /etc/zope.conf $*" \
          </dev/null
    <BLANKLINE>
        ;;
      restart)
    <BLANKLINE>
        ${0} stop
        sleep 1
        ${0} start
    <BLANKLINE>
        ;;
      *) 
    <BLANKLINE>
        su zope -c \
          "/opt/zope/bin/zopectl -C /etc/zope.conf $*" \
          </dev/null
    <BLANKLINE>
        ;;
    esac
    <BLANKLINE>

Note that now the su command is used to run the script.  Because the
script is included in double quotes, it can't contain double
quotes. (The recipe makes no attempt to escape double quotes.)

Also note that now the script must be run as root, so the generated
script checks that root is running it.

If we say the user is root:

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = zoperc
    ...
    ... [zoperc]
    ... recipe = zc.recipe.rhrc
    ... parts = zope
    ... dest = %(dest)s
    ... chkconfig = 345 90 10
    ... chkconfigcommand = echo
    ... user = root
    ...
    ... [zope]
    ... run-script = /opt/zope/bin/zopectl -C /etc/zope.conf
    ... """ % dict(dest=demo))


Then the generated script won't su, but it will still check that root
is running it:

    >>> print system('bin/buildout'),
    buildout: Uninstalling zoperc
    buildout: Running uninstall recipe
    --del zoperc
    buildout: Installing zoperc
    --add zoperc

    >>> cat(demo, 'zoperc')
    #!/bin/sh 
    <BLANKLINE>
    # the next line is for chkconfig
    # chkconfig: 345 90 10
    # description: please, please work
    <BLANKLINE>
    <BLANKLINE>
    if [ $(whoami) != "root" ]; then
      echo "You must be root."
      exit 1
    fi
    <BLANKLINE>
    case $1 in 
      stop)
    <BLANKLINE>
        /opt/zope/bin/zopectl -C /etc/zope.conf $* \
          </dev/null
    <BLANKLINE>
        ;;
      restart)
    <BLANKLINE>
        ${0} stop
        sleep 1
        ${0} start
    <BLANKLINE>
        ;;
      *) 
    <BLANKLINE>
        /opt/zope/bin/zopectl -C /etc/zope.conf $* \
          </dev/null
    <BLANKLINE>
        ;;
    esac
    <BLANKLINE>


A part that defines a run script can also define environment-variable
settings to be used by the rc script by supplying an env option:

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = zoperc
    ...
    ... [zoperc]
    ... recipe = zc.recipe.rhrc
    ... parts = zope
    ... dest = %(dest)s
    ... chkconfig = 345 90 10
    ... chkconfigcommand = echo
    ... user = zope
    ...
    ... [zope]
    ... run-script = /opt/zope/bin/zopectl -C /etc/zope.conf
    ... env = LD_LIBRARY_PATH=/opt/foolib
    ... """ % dict(dest=demo))

    >>> print system('bin/buildout'),
    buildout: Uninstalling zoperc
    buildout: Running uninstall recipe
    --del zoperc
    buildout: Installing zoperc
    --add zoperc

    >>> cat(demo, 'zoperc')
    #!/bin/sh 
    <BLANKLINE>
    # the next line is for chkconfig
    # chkconfig: 345 90 10
    # description: please, please work
    <BLANKLINE>
    <BLANKLINE>
    if [ $(whoami) != "root" ]; then
      echo "You must be root."
      exit 1
    fi
    <BLANKLINE>
    case $1 in 
      stop)
    <BLANKLINE>
        LD_LIBRARY_PATH=/opt/foolib \
          su zope -c \
          "/opt/zope/bin/zopectl -C /etc/zope.conf $*" \
          </dev/null
    <BLANKLINE>
        ;;
      restart)
    <BLANKLINE>
        ${0} stop
        sleep 1
        ${0} start
    <BLANKLINE>
        ;;
      *) 
    <BLANKLINE>
        LD_LIBRARY_PATH=/opt/foolib \
          su zope -c \
          "/opt/zope/bin/zopectl -C /etc/zope.conf $*" \
          </dev/null
    <BLANKLINE>
        ;;
    esac
    <BLANKLINE>

Sometimes, you need to start multiple processes.  You can specify
multiple parts. For example, suppose we wanted to start 2 Zope
instances:

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = zoperc
    ...
    ... [zoperc]
    ... recipe = zc.recipe.rhrc
    ... parts = instance1 instance2
    ... dest = %(dest)s
    ... chkconfig = 345 90 10
    ... chkconfigcommand = echo
    ... user = zope
    ...
    ... [instance1]
    ... run-script = /opt/zope/bin/zopectl -C /etc/instance1.conf
    ... env = LD_LIBRARY_PATH=/opt/foolib
    ...
    ... [instance2]
    ... run-script = /opt/zope/bin/zopectl -C /etc/instance2.conf
    ... env = LD_LIBRARY_PATH=/opt/foolib
    ... """ % dict(dest=demo))

    >>> print system('bin/buildout'),
    buildout: Uninstalling zoperc
    buildout: Running uninstall recipe
    --del zoperc
    buildout: Installing zoperc
    --add zoperc

    >>> cat(demo, 'zoperc')
    #!/bin/sh 
    <BLANKLINE>
    # the next line is for chkconfig
    # chkconfig: 345 90 10
    # description: please, please work
    <BLANKLINE>
    <BLANKLINE>
    if [ $(whoami) != "root" ]; then
      echo "You must be root."
      exit 1
    fi
    <BLANKLINE>
    case $1 in 
      stop)
    <BLANKLINE>
        LD_LIBRARY_PATH=/opt/foolib \
          su zope -c \
          "/opt/zope/bin/zopectl -C /etc/instance2.conf $*" \
          </dev/null
    <BLANKLINE>
        LD_LIBRARY_PATH=/opt/foolib \
          su zope -c \
          "/opt/zope/bin/zopectl -C /etc/instance1.conf $*" \
          </dev/null
    <BLANKLINE>
        ;;
      restart)
    <BLANKLINE>
        ${0} stop
        sleep 1
        ${0} start
    <BLANKLINE>
        ;;
      *) 
    <BLANKLINE>
        LD_LIBRARY_PATH=/opt/foolib \
          su zope -c \
          "/opt/zope/bin/zopectl -C /etc/instance1.conf $*" \
          </dev/null
    <BLANKLINE>
        LD_LIBRARY_PATH=/opt/foolib \
          su zope -c \
          "/opt/zope/bin/zopectl -C /etc/instance2.conf $*" \
          </dev/null
    <BLANKLINE>
        ;;
    esac
    <BLANKLINE>

Now the rc script starts both instances. Note that it stops them in
reverese order.  This isn't so important in a case like this, but
would be more important if a later script depended on an earlier one.

In addition to the zoperc script, we got scripts for each instance:

    >>> ls(demo)
    -  zoperc
    -  zoperc-instance1
    -  zoperc-instance2

    >>> cat(demo, 'zoperc-instance1')
    #!/bin/sh 
    <BLANKLINE>
    # This script is for adminstrator convenience.  It should
    # NOT be installed as a system startup script!
    <BLANKLINE>
    <BLANKLINE>
    if [ $(whoami) != "root" ]; then
      echo "You must be root."
      exit 1
    fi
    <BLANKLINE>
    case $1 in 
      stop)
    <BLANKLINE>
        LD_LIBRARY_PATH=/opt/foolib \
          su zope -c \
          "/opt/zope/bin/zopectl -C /etc/instance1.conf $*"
    <BLANKLINE>
        ;;
      restart)
    <BLANKLINE>
        ${0} stop
        sleep 1
        ${0} start
    <BLANKLINE>
        ;;
      *) 
    <BLANKLINE>
        LD_LIBRARY_PATH=/opt/foolib \
          su zope -c \
          "/opt/zope/bin/zopectl -C /etc/instance1.conf $*"
    <BLANKLINE>
        ;;
    esac
    <BLANKLINE>

The individual scripts don't have chkconfig information.

The zc.recipe.rhrc recipe is designed to work with the
zc.recipe.deployment recipe.  You can specify the name of a deployment
section.  If a deployment section is specified, then that name will be
used for the rc scripts and the user from the deployment section will
be used if a user isn't specified in the rc script's own section:

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = zoperc
    ...
    ... [acme]
    ... user = acme
    ...
    ... [zoperc]
    ... recipe = zc.recipe.rhrc
    ... parts = instance1 instance2
    ... dest = %(dest)s
    ... chkconfig = 345 90 10
    ... chkconfigcommand = echo
    ... deployment = acme
    ...
    ... [instance1]
    ... run-script = /opt/zope/bin/zopectl -C /etc/instance1.conf
    ... env = LD_LIBRARY_PATH=/opt/foolib
    ...
    ... [instance2]
    ... run-script = /opt/zope/bin/zopectl -C /etc/instance2.conf
    ... env = LD_LIBRARY_PATH=/opt/foolib
    ... """ % dict(dest=demo))

    >>> print system('bin/buildout'),
    buildout: Uninstalling zoperc
    buildout: Running uninstall recipe
    --del zoperc
    buildout: Installing zoperc
    --add acme

XXX of course, there is a problem here.  We really should run
chkconfig --del on the old rc script, ut we would need uninstall
recipes and zc.buildout doesn't support those yet.

    >>> ls(demo)
    -  acme
    -  acme-instance1
    -  acme-instance2

    >>> cat(demo, 'acme')
    #!/bin/sh 
    <BLANKLINE>
    # the next line is for chkconfig
    # chkconfig: 345 90 10
    # description: please, please work
    <BLANKLINE>
    <BLANKLINE>
    if [ $(whoami) != "root" ]; then
      echo "You must be root."
      exit 1
    fi
    <BLANKLINE>
    case $1 in 
      stop)
    <BLANKLINE>
        LD_LIBRARY_PATH=/opt/foolib \
          su acme -c \
          "/opt/zope/bin/zopectl -C /etc/instance2.conf $*" \
          </dev/null
    <BLANKLINE>
        LD_LIBRARY_PATH=/opt/foolib \
          su acme -c \
          "/opt/zope/bin/zopectl -C /etc/instance1.conf $*" \
          </dev/null
    <BLANKLINE>
        ;;
      restart)
    <BLANKLINE>
        ${0} stop
        sleep 1
        ${0} start
    <BLANKLINE>
        ;;
      *) 
    <BLANKLINE>
        LD_LIBRARY_PATH=/opt/foolib \
          su acme -c \
          "/opt/zope/bin/zopectl -C /etc/instance1.conf $*" \
          </dev/null
    <BLANKLINE>
        LD_LIBRARY_PATH=/opt/foolib \
          su acme -c \
          "/opt/zope/bin/zopectl -C /etc/instance2.conf $*" \
          </dev/null
    <BLANKLINE>
        ;;
    esac
    <BLANKLINE>

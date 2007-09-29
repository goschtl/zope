Configuration Extensions for Filtering or Inhibiting Configuration
==================================================================

The zc.configuration package provides some configuration directives
for inhibiting configuration.  The first of these is the exclude
directive.  It is used to exclude processing of configuration
files. It is useful when including a configuration that includes some
other configuration that you don't want.  It must be used before
including the files to be excluded.

First, let's look at an example.  The zope.configuration.demo package
has a ZCML configuration that includes some other configuration files.

We'll set a log handler so we can see what's going on:

    >>> import logging, sys
    >>> logger = logging.getLogger('config')
    >>> oldlevel = logger.level
    >>> logger.setLevel(logging.DEBUG)
    >>> handler = logging.StreamHandler(sys.stdout)
    >>> logger.addHandler(handler)
 
Now, we'll include the zc.configuration.demo config:

    >>> from zope.configuration import xmlconfig
    >>> _ = xmlconfig.string('<include package="zc.configuration.demo" />')
    include /zc.configuration/src/zc/configuration/demo/configure.zcml
    include /zc.configuration/src/zc/configuration/demo/sub/configure.zcml
    include /zc.configuration/src/zc/configuration/demo/spam.zcml

Each run of the configuration machinery runs with fresh state, so
rerunning gives the same thing:

    >>> _ = xmlconfig.string('<include package="zc.configuration.demo" />')
    include /zc.configuration/src/zc/configuration/demo/configure.zcml
    include /zc.configuration/src/zc/configuration/demo/sub/configure.zcml
    include /zc.configuration/src/zc/configuration/demo/spam.zcml

Now, we'll load the zc.configuration meta.zcml and use the exclude
directive to exclude the two files included by the configuration file
in zc.configuration.demo:

    >>> _ = xmlconfig.string(
    ... '''
    ... <configure  xmlns="http://namespaces.zope.org/zope">
    ...   <include package="zc.configuration" file="meta.zcml" />
    ...   <exclude package="zc.configuration.demo.sub" />
    ...   <exclude package="zc.configuration.demo" file="spam.zcml" />
    ...   <include package="zc.configuration.demo" />
    ... </configure>
    ... ''')
    include /zc.configuration/src/zc/configuration/meta.zcml
    include /zc.configuration/src/zc/configuration/demo/configure.zcml
    

.. cleanup

    >>> logger.setLevel(oldlevel)
    >>> logger.removeHandler(handler)

;-*-Doctest-*-
=======================
z3c.recipe.ldap package
=======================

.. contents::

What is z3c.recipe.ldap ?
=========================

This recipe can be used to deploy an OpenLDAP server in a
zc.buildout.  More specifically it provides for initializing an LDAP
database from an LDIF file and for setting up an LDAP instance in the
buildout.  This recipe can also be used to provide an isolated LDAP
instance as a test fixture.

How to use z3c.recipe.ldap ?
============================

-------------------------
Installing slapd instance
-------------------------

The default recipe in z3c.recipe.ldap can be used to deploy a slapd
LDAP server in the buildout.  Options in the slapd part not used by
the recipe itself will be used to create and populate a slapd.conf
file.

The only required option is the suffix argupent.  Specifying the
suffix with a dc requires that the "dc" LDAP attribute type
configuration.  Write a buildout.cfg with a suffix and including the
attribute type configuration.  Also specify that the server should use
a socket instead of a network port::

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... parts = slapd
    ...
    ... [slapd]
    ... recipe = z3c.recipe.ldap
    ... use-socket = True
    ... include =
    ...     foo.schema
    ...     bar.conf
    ... suffix = "dc=localhost"
    ... """)

Create the files to be included::

    >>> write(sample_buildout, 'foo.schema',
    ... """
    ... attributetype ( 0.9.2342.19200300.100.1.25
    ... 	NAME ( 'dc' 'domainComponent' )
    ... 	DESC 'RFC1274/2247: domain component'
    ... 	EQUALITY caseIgnoreIA5Match
    ... 	SUBSTR caseIgnoreIA5SubstringsMatch
    ... 	SYNTAX 1.3.6.1.4.1.1466.115.121.1.26 SINGLE-VALUE )
    ... """)
    >>> write(sample_buildout, 'bar.conf', '\n')

Run the buildout::

    >>> print system(buildout),
    Installing slapd.
    Generated script '/sample-buildout/bin/slapd'.

The configuration file is created in the part by default.  Note that
keys that can be specified multiple times in slapd.conf, such as
include, will be constitued from multiple line separated values when
present.  Also note that keys that contain file paths in slapd.conf,
such as include, will be expanded from the buildout directory::

    >>> ls(sample_buildout, 'parts', 'slapd')
    -  slapd.conf
    >>> cat(sample_buildout, 'parts', 'slapd', 'slapd.conf')
    include	/sample-buildout/foo.schema
    include	/sample-buildout/bar.conf...

An empty directory is created for the LDAP database::

    >>> ls(sample_buildout, 'var')
    d  slapd
    >>> ls(sample_buildout, 'var', 'slapd')

A script is also created for starting and stopping the slapd server::

    >>> ls(sample_buildout, 'bin')
    -  buildout
    -  slapd

Start the slapd server::

    >>> bin = join(sample_buildout, 'bin', 'slapd')
    >>> print system(bin+' start'),

On first run, the LDAP database is created::

    >>> ls(sample_buildout, 'var', 'slapd')
    - __db.001...

While the server is running a pid file is created::

    >>> ls(sample_buildout, 'parts', 'slapd')
    -  slapd.conf
    -  slapd.pid

Stop the slapd server::

    >>> print system(bin+' stop'),

Wait for it to shutdown::

    >>> import time
    >>> time.sleep(0.1)

When the slapd server finishes shutting down the pid file is deleted::

    >>> ls(sample_buildout, 'parts', 'slapd')
    -  slapd.conf

Specifying the slapd binary
---------------------------

The slapd binary to be used can be specified.  A buildout could, for
example, include a part using a CMMI recipe and use the slapd binary
from that build.

Before specifying the slapd to use, it's left up to the environment::

    >>> cat(sample_buildout, '.installed.cfg')
    [buildout]...
    [slapd]...
    slapd = slapd...

Specify a slapd in the buildout.cfg::

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... parts = slapd
    ...
    ... [slapd]
    ... recipe = z3c.recipe.ldap
    ... slapd = /usr/sbin/slapd
    ... use-socket = True
    ... include =
    ...     foo.schema
    ...     bar.conf
    ... suffix = "dc=localhost"
    ... """)

Run the buildout::

    >>> print system(buildout),
    Uninstalling slapd.
    Installing slapd.
    Generated script '/sample-buildout/bin/slapd'.

Now it uses the specific slapd binary::

    >>> cat(sample_buildout, '.installed.cfg')
    [buildout]...
    [slapd]...
    slapd = /usr/sbin/slapd...

----------------------------
Initalizing an LDAP database
----------------------------

In the simplest form, simply provide an ldif arguemnt in the part with
one or more filenames.

    >>> write(sample_buildout, 'foo.ldif',
    ... """
    ... olcAttributeTypes: ( 0.9.2342.19200300.100.1.25
    ...   NAME ( 'dc' 'domainComponent' )
    ...   DESC 'RFC1274/2247: domain component'
    ...   EQUALITY caseIgnoreIA5Match
    ...   SUBSTR caseIgnoreIA5SubstringsMatch
    ...   SYNTAX 1.3.6.1.4.1.1466.115.121.1.26 SINGLE-VALUE )
    ... """)

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... parts = slapd slapadd
    ...
    ... [slapd]
    ... recipe = z3c.recipe.ldap
    ... include =
    ...     foo.schema
    ... suffix = "dc=localhost"
    ...
    ... [slapadd]
    ... recipe = z3c.recipe.ldap:slapadd
    ... conf = ${slapd:conf}
    ... ldif = foo.ldif
    ... """)

    >>> print system(buildout),
    Uninstalling slapd.
    Installing slapd.
    Generated script '/sample-buildout/bin/slapd'.
    Installing slapadd.

Multiple LDIF files can be specified::

    >>> TODO

An alternate open ldap instance directory can be specified in the
'directory' option::

    >>> TODO
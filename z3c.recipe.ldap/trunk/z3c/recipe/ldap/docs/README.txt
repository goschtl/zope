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
configuration.  Write a buildout.cfg with a suffix and include
core.schema for the attribute type configuration.  Also specify that
the server should use a socket instead of a network port::

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... parts = slapd
    ...
    ... [slapd]
    ... recipe = z3c.recipe.ldap
    ... slapd = %(openldap)s/libexec/slapd
    ... use-socket = True
    ... include =
    ...     %(openldap)s/etc/openldap/schema/core.schema
    ...     foo.schema
    ...     bar.conf
    ... modulepath = 
    ... moduleload = 
    ... suffix = "dc=localhost"
    ... """ % globals())

Create the files to be included::

    >>> write(sample_buildout, 'foo.schema', '\n')
    >>> write(sample_buildout, 'bar.conf', '\n')

Run the buildout::

    >>> print system(buildout),
    Installing slapd.
    Generated script '/sample-buildout/bin/slapd'.

The configuration file is created in the part by default.  Note that
keys that can be specified multiple times in slapd.conf, such as
include, will be constitued from multiple line separated values when
present.  Also note that keys that contain file paths in slapd.conf,
such as include, will be expanded from the buildout directory.
Finally note that options specified with blank values will be
excluded::

    >>> ls(sample_buildout, 'parts', 'slapd')
    -  slapd.conf
    >>> cat(sample_buildout, 'parts', 'slapd', 'slapd.conf')
    include	.../etc/openldap/schema/core.schema
    include	/sample-buildout/foo.schema
    include	/sample-buildout/bar.conf
    pidfile	/sample-buildout/parts/slapd/slapd.pid
    database	bdb
    suffix	"dc=localhost"
    directory	/sample-buildout/var/slapd
    dbconfig	set_cachesize	0	268435456	1
    dbconfig	set_lg_regionmax	262144
    dbconfig	set_lg_bsize	2097152
    index	objectClass	eq

The socket path is properly escaped in the configuration::

    >>> cat(sample_buildout, '.installed.cfg')
    [buildout]...
    [slapd]...
    urls = ldapi://...%2Fsample-buildout%2Fparts%2Fslapd%2Fslapd.socket
    ...

An empty directory is created for the LDAP database::

    >>> ls(sample_buildout, 'var')
    d  slapd
    >>> ls(sample_buildout, 'var', 'slapd')

A script is also created for starting and stopping the slapd server::

    >>> ls(sample_buildout, 'bin')
    -  buildout
    -  slapd

Start the slapd server::

    >>> import time
    >>> bin = join(sample_buildout, 'bin', 'slapd')
    >>> print system(bin+' start'),
    >>> time.sleep(0.1)

On first run, the LDAP database is created::

    >>> ls(sample_buildout, 'var', 'slapd')
    -  DB_CONFIG
    -  __db.001...

While the server is running a pid file is created and also a socket in
this case::

    >>> ls(sample_buildout, 'parts', 'slapd')
    -  slapd.conf
    -  slapd.pid
    -  slapd.socket

Stop the slapd server::

    >>> print system(bin+' stop'),
    >>> time.sleep(0.1)

When the slapd server finishes shutting down the pid file is deleted::

    >>> ls(sample_buildout, 'parts', 'slapd')
    -  slapd.conf

The slapd binary
----------------

The slapd binary to be used can be specified as we did above when we
specified the slapd binary from the buildout OpenLDAP CMMI part::

    >>> cat(sample_buildout, '.installed.cfg')
    [buildout]...
    [slapd]...
    slapd = .../parts/openldap/libexec/slapd
    ...

If no binary is specified, it's left up to the environment.
Write a buildout.cfg with no slapd specified::

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... parts = slapd
    ...
    ... [slapd]
    ... recipe = z3c.recipe.ldap
    ... use-socket = True
    ... """)

Run the buildout::

    >>> print system(buildout),
    Uninstalling slapd.
    Installing slapd.
    Generated script '/sample-buildout/bin/slapd'.

Now it will find the binary on the system path::

    >>> cat(sample_buildout, '.installed.cfg')
    [buildout]...
    [slapd]...
    slapd = slapd
    ...

----------------------------
Initalizing an LDAP database
----------------------------

The z3c.recipe.ldap.Slapadd can be used initialize an LDAP database
from an LDIF file.  In the simplest form, simply provide an "ldif"
option in the part with one or more filenames.

Write a buildout.cfg that lists some LDIF files::

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... parts = slapd slapadd
    ...
    ... [slapd]
    ... recipe = z3c.recipe.ldap
    ... include =
    ...     %(openldap)s/etc/openldap/schema/core.schema
    ...     %(openldap)s/etc/openldap/schema/cosine.schema
    ... modulepath = 
    ... moduleload = 
    ... suffix = "dc=localhost"
    ...
    ... [slapadd]
    ... recipe = z3c.recipe.ldap:slapadd
    ... slapadd = %(openldap)s/sbin/slapadd
    ... conf = ${slapd:conf}
    ... ldif =
    ...     dc.ldif
    ...     admin.ldif
    ... """ % globals())

Write the LDIF files::

    >>> write(sample_buildout, 'dc.ldif',
    ... """
    ... dn: dc=localhost
    ... dc: localhost
    ... objectClass: top
    ... objectClass: domain
    ... """)
    >>> write(sample_buildout, 'admin.ldif',
    ... """
    ... dn: cn=admin,dc=localhost
    ... objectClass: person
    ... cn: admin
    ... sn: Manager
    ... """)

Run the buildout::

    >>> print system(buildout),
    Uninstalling slapd.
    Installing slapd.
    Generated script '/sample-buildout/bin/slapd'.
    Installing slapadd.

The entries have been added to the LDAP database::

    >>> print system(os.path.join(openldap, 'sbin', 'slapcat')+' -f '+
    ...        os.path.join(sample_buildout,
    ...                     'parts', 'slapd', 'slapd.conf')),
    dn: dc=localhost
    dc: localhost
    objectClass: top
    objectClass: domain...
    dn: cn=admin,dc=localhost
    objectClass: person
    cn: admin
    sn: Manager...

The LDIF files are added on update also.

Remove the existing LDAP database::

    >>> rmdir(sample_buildout, 'var', 'slapd')
    >>> mkdir(sample_buildout, 'var', 'slapd')

Run the Buildout to add the LDIF files again::

    >>> print system(buildout),
    Updating slapd.
    Updating slapadd.

The entries have been added to the LDAP database::

    >>> print system(os.path.join(openldap, 'sbin', 'slapcat')+' -f '+
    ...        os.path.join(sample_buildout,
    ...                     'parts', 'slapd', 'slapd.conf')),
    dn: dc=localhost
    dc: localhost
    objectClass: top
    objectClass: domain...
    dn: cn=admin,dc=localhost
    objectClass: person
    cn: admin
    sn: Manager...

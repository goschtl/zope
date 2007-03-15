===========================================
Secure FTP (SFTP) Extension for zc.buildout
===========================================

The zc.buildoutsftp package provides a zc.buildout extension that
provides support for SFTP.  To use it, simply provide the option::

  extension = zc.buildoutsftp 

in your buildout section. Then you can use sftp URLs for fine-links or
index URLs. (Note that zc.buildout >=1.0.0b5 is needed for this to
work properly.)

An SFTP URL is similar to an FTP URL and is of the form::

  sftp://user:password@hostname:port/path

where the user name, password, and port are optional.  Here are some
examples:

The following URL accesses the path /distribution on download.zope.org::

  sftp://download.zope.org/distribution

The following URL accesses the path /distribution on download.zope.org
using the user id jim::

   sftp://jim@download.zope.org/distribution

The following URL accesses the path /distribution on download.zope.org
using the user id jim and password 123::

  sftp://jim:123@download.zope.org/distribution


The following url accesses the path /distribution on download.zope.org
using an ssh server running on port 1022::

  sftp://download.zope.org:1022/distribution

The buildout extension actually installs a urllib2 handler for the
"sftp" protocol.  This handler is actually setuptools specific because
it generates HTML directory listings, needed by setuptools and makes
no effort to make directory listings useful for anything else.
It is possible that, in the future, setuptools will provide it's own
extension mechanism for handling alternate protocols, in which case,
we might bypass the urllib2 extension mechanism.

SSH Compatibility
=================

The extension works with Open SSH on unix-based systems and PuTTY on
Windows.  Unless a password is given in the URL, private keys are
ontained from ssh agent (pagent on Windows).

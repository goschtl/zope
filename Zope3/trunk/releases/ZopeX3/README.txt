=======
Zope X3
=======

Welcome to the Zope X3 source distribution!

Zope X3 is the next major Zope release and has been written from
scratch based on the latest software design patterns and the
experiences of Zope 2.  The "X" in the name stands for "experimental",
since this release does not try to provide any backward-compatibility
to Zope 2.


Requirements
------------

Zope X3 requires that Python 2.3.3 or newer be installed.


Building and installing the software
------------------------------------

Unix
~~~~

Zope X3 is built using the conventional "configure" / "make" dance on
Unix and Linux.  There are only a couple of options to the configure
script, but you shouldn't need either of them in the common case.  The
configure script will attempt to locate the available Python
installations and pick the best one for use with Zope:

  $ ./configure

  Configuring Zope 3 installation

  Testing for an acceptable Python interpreter...

  Python version 2.4a0 found at /usr/local/bin/python
  Python version 2.3.4 found at /usr/local/bin/python2.3

  The optimum Python version (2.3.4) was found at /usr/local/bin/python2.3.

If you want to specify which Python should be used with Zope, use the
"--with-python" option to indicate the specific Python interpreter to
use:

  $ ./configure --with-python /opt/Python-2.3.4/bin/python

  Using Python interpreter at python2.3

  Configuring Zope 3 installation

The default installation directory for Zope is
/usr/local/ZopeX3-<version>, where <version> is replaced with the
version of Zope X3 you're installing; it will match the version number
from the compressed tarball you unpacked.  To change the installation
directory, use the "--prefix" option to specify an alternate location:

  $ ./configure --prefix /opt/ZopeX3-3.0.0

  Configuring Zope 3 installation

  Testing for an acceptable Python interpreter...

  Python version 2.4a0 found at /usr/local/bin/python
  Python version 2.3.4 found at /usr/local/bin/python2.3

  The optimum Python version (2.3.4) was found at /usr/local/bin/python2.3.

Once you've configured Zope, you can build the software using "make".
No options are needed.

  $ make
  python2.3 install.py -q build

Now that the software has been built, you can run the unit tests for
the software to make sure that everything is working on your
platform.  This is an optional step, and can take a while to
complete.  The tests can be run using "make" as well:

  $ make check
  python2.3 install.py -q build
  python2.3 test.py -v
  Running UNIT tests at level 1
  Running UNIT tests from /home/user/ZopeX3-3.0.0a1/build/lib.linux-i686-2.3
  [...lots of dots, one per test...]
  ----------------------------------------------------------------------
  Ran 4510 tests in 501.389s

  OK

The line before the final "OK" tells how many individual tests were
run, and long it took to run them.  These numbers will vary based on
release, operating system, and host platform.

To install the software, run "make" again:

  $ make install
  python2.3 install.py -q build
  python2.3 install.py -q install --home "/opt/ZopeX3-3.0.0"

You now have a complete Zope X3 installation.


Windows
~~~~~~~

XXX to be written


Creating a Zope instance home
-----------------------------

XXX to be written


Starting Zope
-------------

XXX to be written


Where to get more information
-----------------------------

For more information about Zope 3, consult the Zope 3 project pages on
the Zope community website:

  http://dev.zope.org/Zope3/

The information there includes links to relevant mailing lists and IRC
forums.

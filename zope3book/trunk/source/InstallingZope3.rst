Installing Zope 3
-----------------


Difficulty
::::::::::

Newcomer


Skilla
::::::

-   You should know how to use the command line of your operating system.
    (For Windows releases, the Installer is provided.)
-   You need to know how to successfully install the latest version of
    Python on your system.


Problem/Task
::::::::::::

Before you can develop anything for Zope 3, you should, of course, install
it.


Solution
::::::::


Zope 3 Installation Requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Zope 3 usually requires the latest stable Python version. For the Zope X3
3.0.0 release, this is Python 2.3.4 or better. Note that you should always
use the latest bug-fix release. Zope 3 does not require you to install or
activate any special packages; the stock Python is fine. This has the great
advantage that you can use a pre-packaged Python distribution (for example
RPM, deb, Windows Installer) for your favorite operating system.

Note: While distutils is part of the standard Python distribution, packagers
often treat it as a separate installation package. In order to install Zope
3, your Python must have distutils installed as well.

The only catch is that Zope 3's C modules must be compiled with the same C
compiler as Python. For example, if you install the standard Python
distribution on Windows, which is compiled with Visual C++ 7, you cannot
compile Zope 3's modules with Cygwin. However, this problem is not as bad as
it seems. The Zope 3 binary distributions are always compiled with the same
compiler as the standard Python distribution for the operating system.
Furthermore, if you want to compile everything yourself, you are likely to
use only one compiler anyway.

On Unix/Linux your best bet is  `gcc`_. All Zope 3 developers are using
`gcc`_, so it will always be supported. Furthermore, all Linux Python
distribution packages are compiled using  `gcc`_. In Windows, the standard
Python distribution is compiled using Visual C++ 7, as mentioned previously.
Therefore the Zope 3 binary Windows release is also compiled with that
compiler. However, people have also successfully used  `gcc`_ by using
Cygwin, which comes with Python. Finally, you can run Zope 3 on MacOS X as
well. All you need are  `gcc`_ and the  `make` program. With these, both
Python and Zope 3 compile just fine.

Python is available at the Python Web site (  `www.python.org`_).


Installing Zope from SVN
~~~~~~~~~~~~~~~~~~~~~~~~

In order to check out Zope 3 from SVN, you need to have a SVN client
installed on your system. If you do not have a SVN account, you can use the
anonymous user to check out a sandbox:


1  svn co svn://svn.zope.org/repos/main/Zope3/trunk Zope3

After the checkout is complete, you enter the Zope 3 directory:


1  cd Zope3

From there you run  `make` (so you need to have  `make` installed, and it
should be available for all mentioned environments). If your Python
executable is not called  `python2.3`_ and/or your Python binary is not in
the path, you need to edit the first line of the  `Makefile`_ file to contain
the correct path to the Python binary. Then you just run make, which
builds/compiles Zope 3:


1  make

Next you copy  `sampleprincipals.zcml`_ to  `principals.zcml`_ and add a user
with manager rights, as follows:


1  <principal
2      id="zope.userid" title="User Name Title"
3      login="username" password="passwd" />
4
5  <grant role="zope.Manager" principal="zope.userid" />

In the preceding code block, note the following:

-   Line 2: Notice that you do not need  `zope.`_ as part of your
    principal ID, but the ID must contain at least one dot (  `.`_), because
    that signals a valid ID.
-   Line 3: The login and password strings can be any random value, but
    they must be correctly encoded for XML.
-   Line 5: If you do not use the default security policy, you might not
    be able to use this  `zope:grant`_ directive because it might not support
    roles. However, if you use the plain Zope 3 checkout, roles are available
    by default.

During development, you often do not want to worry about security. In such a
case you can simply give  `anybody`_ the  `Manager`_ role:


1  <grant role="zope.Manager" principal="zope.anybody" />

The fundamental application server configuration can be found in
`zope.conf`_. If  `zope.conf`_ is not available,  `zope.conf.in`_ is used
instead. In this file you can define the types and ports of the servers you
would like to activate, setup the ZODB storage type and specify logging
options. The configuration file is very well documented, and making the
desired changes should be easy.

Now you are ready to start Zope 3 for the first time:


1  ./bin/runzope

The following output text should appear::

  ------
  2003-06-02T20:09:13 INFO PublisherHTTPServer zope.server.http (HTTP)
   started.
          Hostname: localhost
          Port: 8080
  ------
  2003-06-02T20:09:13 INFO PublisherFTPServer zope.server.ftp started.
          Hostname: localhost
          Port: 8021
  ------
   2003-06-02T20:09:13 INFO root Startup time: 5.447 sec real, 5.190 sec
     CPU

After Zope comes up, you can test the servers by typing the following URL in
your browser:  `http://localhost:8080/`_. You can test FTP by using
`ftp://username@localhost:8021/`_. Even WebDAV is available using
`webdav://localhost:8080/`_ in Konqueror or your favorite WebDAV client.

An XML-RPC server is also built in to Zope by default, but most objects do
not support any XML-RPC methods, so you cannot test it right away. Chapter
"??" provides detailed instructions on how to use the XML-RPC server.


Installing the Source Distribution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

e following sections describe how to use the source TAR ball to compile and
install a Zope 3 distribution.


Unpacking the Package
:::::::::::::::::::::

The latest release of Zope 3 can be found at
`www.zope.org/Products/ZopeX3`_. First, you need to download the latest Zope
3 release by clicking the file that is available for all platforms, i.e.
`ZopeX3-VERSION.tgz`_. You can use  `tar`_ or WinZip to extract the archive,
like this:


1  tar xzf ZopeX3-3.0.0.tgz


Building Zope
:::::::::::::

For Zope 3 releases, distributation makers provided the well-known
`configure`_/  `make` procedure. So you can start the configuration process
by using the following after you have entered the newly created directory:


1  ./configure

If you want to place the binaries of the distribution somewhere other than
`/usr/local/ZopeX3-VERSION`_, you can specify the  `-prefix`_ option as
usual. Also, if you have Python installed at a non-standard location, you can
specify the Python executable by using  `-with-python`_. A full configuration
statement could look like this:


1  ./configure --prefix=/opt/Zope3 --with-
    python=/opt/puython2.3/bin/python2.3

The following output is immediately returned:


1  Configuring Zope X3 installation
2
3  Using Python interpreter at /opt/puython2.3/bin/python2.3

Now that the source has been configured, you can build it by using  `make`.
After you enter the  `make` command, the following line is returned:


1  /opt/python2.3/bin/python2.3 install.py -q build

The hard drive is busy for several minutes, compiling the source. When the
command line returns, you can run the tests by using the following:


1  make check

Here, both the unit and functional tests are executed. For each executed
test, you have one dot on the screen. The check takes between 5 and 10
minutes depending on the speed and free cycles on your computer. The final
output should look as follows::


  Python2.3 install.py -q build
  Python2.3 test.py -v
  Running UNIT tests at level 1
  Running UNIT tests from
   /path/to/ZopeX3-VERSION/build/lib.linux-i686-2.3
  [some 4000+ dots]
  ----------------------------------------------------------------------
  Ran 3896 tests in 696.647s

  OK

The exact number of tests run depends on the version of Zope, the operating
system, and the host platform. If the last line displays  `OK`_, you know
that all tests passed. After you have verified the check, you can install the
distribution as follows:


1  make install

Note: You have to have the correct permissions to create the installation
directory and copy the files into it. Thus, it might be useful to become root
to execute the command.


Creating a Zope Instance
::::::::::::::::::::::::

When the installation is complete, Zope is available in the directory you
specified in  `-prefix`_ or under  `/usr/local/ZopeX3-VERSION`_. However,
Zope will not yet run, because you have not created an instance yet. You use
instances when you want to host several Zope-based sites, using the same base
software configuration.

Creating a new instance is easy. You enter the Zope 3 installation directory
and enter the following command:


1  /bin/mkzopeinstance -u username:password -d path/to/instance

This creates a Zope 3 instance in  `path/to/instance`_. A user who has the
login  `username`_ and password  `password`_ is created for you, and the
`zope.manager`_ role is assigned to it. All the configuration for the created
instance are available in the  `path/to/instance/etc`_ directory. You need to
review all the information in there to ensure that it fits your needs.


Running Zope
::::::::::::

You execute Zope by calling


1  ./bin/runzope

from the instance directory. The startup output will be equal to that of the
source Zope SVN installation.

You are all done now! When the server is up and running, you can test it via
you favorite browser, as described earlier in this chapter.


Installing the Source Distribution in Windows Without Using make
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Installing the source distribution on Windows is possible even without
`make`. However, you need a supported C compiler to build the package. If
you do not have a C compiler or Cygwin installed, you can use the Windows
Installer to install Zope 3. (See the next section for more details.)

Before installing Zope 3, you need to install Python 2.3.4 or higher. On
Windows NT/2000/XP the extension  `.py`_ is automatically associated with the
Python executable, so you do not need to specify the Python executable when
running a script.

After you unpack the distribution, you enter the directory. You build the
software by using this:


1  install.py -q build

When the build process is complete, you can run the tests with this:


1  test.py -v

This should give you the same output as under Unix/Linux. After the tests are
verified, you install the distribution by using the following command:


1  install.py -q install

You have now completed the installation of Zope 3. Now you can follow the
final steps in the previous section to create an instance and start up Zope.

Note: When you install Zope 3 in Windows without using  `make`, it's really
hard to uninstall it later, because you have to manually delete files and
directories from various locations, including your Python's  `Lib/site-
packages"` and  `Scripts` directories. You also have to completely remove
the  `zopeskel` directory. If you use Windows Installer instead, an
uninstallation program is provided and registered in the Control Panel's
Add/Remove Programs applet.


Installing the Binary Distribution of Zope
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Currently binary releases of Zope are available only for Windows. These
releases assume that you have the standard Windows Python release installed.
The Windows binary release is an executable that automatically executes
Windows Installer. The first task is to make sure that you have the correct
Python version installed. Zope X3.0 is released to work with Python 2.3.
Thus, you need to install the latest Python 2.3 bug fix release. You can get
the Windows binary installer at  `www.python.org/download/`_.

If you already have a previous version of Zope X3, you need to remove it by
using Add/Remove Programs from the Control Panel. Then you can install the
Zope X3.0 release, which you can find at  `dev.zope.org/Zope3/Downloads`_.
After you download it, you simply execute the installer and follow its
instructions.

When the install is complete, you need to open a Windows command prompt and
change to the root Python 2.3 directory, usually  `C:\python23`. Then you
execute the instance creation script using this:


1  .\python .\Scripts\mkzopeinstance -u username:password -d
    c:\path\to\instance

This completes the installation. You can now run Zope 3 by using this:


1  .\python c:\path\to\instance\bin\runzope

The instance's  `bin`_ directory also contains some other useful scripts,
such as the test runner.

You can later use the Control Panel's Add/Remove Programs applet to uninstall
Zope 3 again.

.. _gcc: gcc
.. _www.python.org: www.python.org
.. _python2.3: python2.3
.. _Makefile: Makefile
.. _sampleprincipals.zcml: sample_principals.zcml
.. _principals.zcml: principals.zcml
.. _zope.: zope.
.. _.: .
.. _zope:grant: zope:grant
.. _anybody: anybody
.. _Manager: Manager
.. _zope.conf: zope.conf
.. _zope.conf.in: zope.conf.in
.. _http://localhost:8080/: http://localhost:8080/
.. _ftp://username@localhost:8021/: ftp://username@localhost:8021/
.. _webdav://localhost:8080/: webdav://localhost:8080/
.. _www.zope.org/Products/ZopeX3: www.zope.org/Products/ZopeX3
.. _ZopeX3-VERSION.tgz: ZopeX3-VERSION.tgz
.. _tar: tar
.. _configure: configure
.. _/usr/local/ZopeX3-VERSION: /usr/local/ZopeX3-VERSION
.. _-prefix: --prefix
.. _-with-python: --with-python
.. _OK: OK
.. _path/to/instance: path/to/instance
.. _username: username
.. _password: password
.. _zope.manager: zope.manager
.. _path/to/instance/etc: path/to/instance/etc
.. _.py: .py
.. _www.python.org/download/: www.python.org/download/
.. _dev.zope.org/Zope3/Downloads: dev.zope.org/Zope3/Downloads
.. _python23: c:\python23\
.. _bin: bin

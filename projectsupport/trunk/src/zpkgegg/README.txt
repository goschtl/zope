zpkgegg
=======

zpkgegg is a Python script which generates a "standard" setup.py from
a package configured to use zpkg as a packaging mechanism.  The
default behavior is to assemble the pieces from the package, along
with the generated setup.py script, and generate egg and sdist
packages.  


Using zpkgegg
-------------

zpkgegg depends on the ''project-template'' from projectsupport
project in the Zope Subversion repository.  Unless overridden by a
command-line parameter, zpkgegg will look for ''project-template'' in
the same relative location as it exists in version control.

As an example, let us consider generating eggs from portions of the
Zope 3 Subversion repository:

  $ svn co svn+ssh://svn.zope.org/repos/main/projectsupport/trunk \
    projectsupport 
  $ svn co svn+ssh://svn.zope.org/repos/main/Zope3/trunk Zope3
  
  $ cd Zope3/src/zope
  $ python ../../../projectsupport/src/zpkgegg/zpkgegg.py interface
    testing exceptions deprecation
  $ ls ./eggs
    zope.interface-1.0.dev_r65726-py2.4-linux-i686.egg
    zope.interface-1.0.dev-r65726.tar.gz
    ...

Behavoral aspects of note:

 * unless otherwise specified, zpkgegg will create an ''eggs''
   directory in the present location
 * you can specify multiple directories on the same command line
 * all generated eggs are marked as non-zip-safe, which tells
   easy_install to expand the eggs when they are installed

Using the eggs
--------------

We can use the eggs by "installing" them.  The installation process
simply creates a .pth file containing the eggs to be placed on the
PYTHONPATH.  We often do _not_ want the .pth file to be placed in the
system site-packages directory, perhaps because we are experimenting
with packages.  Continuing our example session:

  $ mkdir localsite
  $ PYTHONPATH=./localsite/ easy_install -d ./localsite/ -S \
    ./localsite/  -f ./eggs zope.interface

This command line instructs easy_install to install zope.interface and
any dependencies into the ''./localsite'' directory, looking in
''./eggs'' for any egg or source packages necessary.  You can also
specify a URL there, such as http://download.zope.org/distribution.
After running the command, we see a .pth file has been created in
./localsite: 

  $ ls ./localsite
  $ cat ./localsite/easy-install.pth
    /.../Zope3/src/zope/eggs/zope.interface-1.0.dev_r65726-py2.4-linux-i686.egg
    /.../Zope3/src/zope/eggs/zope.testing-1.0.dev_r65726-py2.4.egg
    /.../Zope3/src/zope/eggs/zope.exceptions-1.0.dev_r65726-py2.4.egg
    /.../Zope3/src/zope/eggs/zope.deprecation-1.0.dev_r65726-py2.4.egg

We see that easy_install has not copied the eggs into localsite, but
rather placed links to the egg files in the .pth file.  We can utilize
these newly installed eggs:

  $ PYTHONPATH=./localsite/ python
  Python 2.4.2 (#2, Jan 17 2006, 12:48:19)
  [GCC 4.0.3 20060115 (prerelease) (Ubuntu 4.0.2-7ubuntu1)] on linux2
  Type "help", "copyright", "credits" or "license" for more information.
  >>> import zope.interface
  >>> zope.interface.__file__
  '/home/nathan/z/Zope3/src/zope/eggs/zope.interface-1.0.dev_r65726-py2.4-linux-i686.egg/zope/interface/__init__.pyc'


Command Line Parameters
-----------------------

  $ zpkgegg.py --help
  usage: zpkgegg.py [options] <source directory>

  options:
    -h, --help            show this help message and exit
    -p PROJECT_TEMPLATE, --template=PROJECT_TEMPLATE
                          Directory containing the project template.
    -w WORKDIR, --working=WORKDIR
                          Working directory for project build out.
    -s SETUP, --setup=SETUP
                          Template to use for generating setup.py.
    -v VERSION, --version=VERSION
                          Version of the package.
    -e EGGDIR, --eggdir=EGGDIR
                          Directory to store eggs in.
    -t, --tree            Only build the project tree.
    -n, --nodelete        Do not delete the source tree after building
                          packages.


References
----------

  - Docs for EasyInstall:
    http://peak.telecommunity.com/DevCenter/EasyInstall

  - Docs for setuptools:
    http://peak.telecommunity.com/DevCenter/setuptools

  - Docs for eggs:
    http://peak.telecommunity.com/DevCenter/PythonEggs

  - zpkg:
    http://...

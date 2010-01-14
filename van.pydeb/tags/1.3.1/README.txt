Tools for introspecting Python package metadata and translating the resulting
information into Debian metadata. This information is translated:

* Setuptools version numbers to Debian format that sorts correctly
* Setuptools package names to Debian binary and source package names
* Setuptools dependencies to Debian dependencies

This package provides a ``van-pydeb`` binary which provides a way to access the
information from shell scripts. A python based API is also available for python
programs to use.

Usage
=====

To extract the dependency info of this package, one can run the following
command after setting up buildout::

    $ ./bin/van-pydeb depends --egg-info van.pydeb.egg-info
    python-setuptools, python-van

This information can then used in a debian/rules file as follows::

    (echo -n 'setuptools:Depends=' && van-pydeb depends --egg-info debian/$(PACKAGE)/usr/lib/python$*/site-packages/$(EGG_NAME).egg-info) >> debian/$(PACKAGE).substvars

There ary many different methods of using this command, such as getting the
dependencies (including the extra dependencies) of the package::

    van-pydeb depends --egg-info debian/$(PACKAGE)/usr/lip/python$*/$(EGG_NAME).egg-info

Or, the dependencies of an extra::

    van-pydeb depends --egg-info debian/$(PACKAGE)/usr/lip/python$*/$(EGG_NAME).egg-info --extra $(EXTRA)

The dependencies of 2 extras::
    
    van-pydeb depends --egg-info debian/$(PACKAGE)/usr/lip/python$*/$(EGG_NAME).egg-info --extra $(EXTRA) --extra $(EXTRA2)

The dependencies of a package excluding the dependencies of extras::

    van-pydeb depends --egg-info debian/$(PACKAGE)/usr/lip/python$*/$(EGG_NAME).egg-info --exclude-extra $(EXTRA1) --exclude-extra $(EXTRA2)

Development
===========

The code for van.pydeb is housed in subversion at http://svn.zope.org/van.pydeb/.

PyDebDep
========

Tools for introspecting egg-info directories and translating the resulting
information into debian format. This information is translated:

    * Setuptools version numbers to debian format that sorts correctly
    * Setuptools package names to debian binary and source package names
    * Setuptools dependencies to debian dependencies

This package provides a script ``van-pydeb`` which introspects an installed
.egg-info to extract egg dependency information. The package names are
converted to their debian equivilant and the dependency information is printed
in the format of a dpkg "Depends:" line.

Usage
-----

To extract the dependency info of this package, one can::

    $ python2.4 setup.py build
    $ PYTHONPATH=./src python2.4 van-pydeb --depends --egg_info src/vanguardistas.van-pydeb.egg-info
    python-setuptools, python-vanguardistas

This information can then used in a debian/rules file as follows:

    i="$$(van-pydeb depends --egg-info debian/$(PACKAGE)/usr/lib/python$*/site-packages/$(EGG_NAME).egg-info)" && echo "setuptools:Depends=$$i" >> debian/$(PACKAGE).substvars

The different methods of using this are:

Give the dependencies (including the extra dependencies) of the package:

    van-pydeb depends --egg-info debian/$(PACKAGE)/usr/lip/python$*/$(EGG_NAME).egg-info

The dependencies of an extra:

    van-pydeb depends --egg-info debian/$(PACKAGE)/usr/lip/python$*/$(EGG_NAME).egg-info --extra $(EXTRA)

The dependencies of 2 extras:
    
    van-pydeb depends --egg-info debian/$(PACKAGE)/usr/lip/python$*/$(EGG_NAME).egg-info --extra $(EXTRA) --extra $(EXTRA2)

The dependencies of a package excluding the dependencies of extras:

    van-pydeb depends --egg-info debian/$(PACKAGE)/usr/lip/python$*/$(EGG_NAME).egg-info --exclude-extra $(EXTRA1) --exclude-extra $(EXTRA2)

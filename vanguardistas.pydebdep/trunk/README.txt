PyDebDep
========

Tools for introspecting egg dependency information and providing the resulting
data to Debian packaging tools.

This package provides a script ``pydebdep`` which introspects an installed
.egg-info to extract egg dependency information. The package names are
converted to their debian equivilant and the dependency information is printed
in the format of a dpkg "Depends:" line.

Usage
-----

To extract the dependency info of this package, one can::

    $ python2.4 setup.py build
    $ PYTHONPATH=./src python2.4 pydebdep --depends --egg_info src/vanguardistas.pydebdep.egg-info
    python-setuptools, python-vanguardistas

This information is then used in a debian/rules file. Included in this package
(in the rules directory) are debian/rules files for simple situations. They are
generic, and work for a lot of packages. But if they don't work for yours, make
your own. 

They can be used in a debian/rules file as follows::

    #!/usr/bin/make -f

    EGG_NAME=vanguardistas.pydebdep
    PACKAGE=python-vanguardistas.pydebdep
    DEB_SETUPTOOLS=pydebdep

    include /usr/lib/python-vanguardistas.pydebdep/rules/rules.1

Future Development
------------------

Er, there shouldn't be much, unless someone finds something big.

Mostly what should change is the mapping of setuptools names to debian package
names as more are added.

This package used to provide a pluggable replacement of ObjectCopier class
and locationCopy function from zope.copypastemove and zope.location
respectively. Currently, all its functionality is merged to those packages
and the new zope.copy package is provided that contains the actual pluggable
copying mechanism used to be in this package with no dependencies except
zope.interface.

This package now only provides backward-compatibility imports and should
not be used for new developments.

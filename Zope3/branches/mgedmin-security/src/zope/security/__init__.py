#
# This file is necessary to make this directory a package.


# XXX There's a circular import problem with the proxy package.
# The proxy framework needs some refactoring, but not today.
import zope.proxy

# Python datetime prototype,

# This package contains the prototype datetime module that will be included
# in Python 2.3.  We've turned it into a package to make it easier to
# deal with in CVS for now.  This __init__ file makes the package look
# like the eventual module.

from _datetime import MINYEAR, MAXYEAR
from _datetime import timedelta
from _datetime import time, timetz
from _datetime import date, datetime, datetimetz
# XXX Temporary, to allow the tests to pass.  This will be replaced by the
# XXX C datetime code (and much larger test suite) soon, where it isn't needed.
from _datetime import _ymd2ord, _ord2ymd, tmxxx
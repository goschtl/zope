# Python datetime `prototype

# This package contains the prototype datetime module that will be included
# in Python 2.3.  We've turned it into a package to make it easier to
# deal with in CVS for now.  This __init__ file makes the package look
# like the eventual module.

from _datetime import timedelta, date, datetime, datetimetz

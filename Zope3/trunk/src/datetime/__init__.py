# Python datetime prototype.

# This package contains the prototype datetime Python module whose C
# version is included in Python 2.3.  We've turned it into a package to
# make it easier to deal with in CVS for now.  This __init__ file makes the
# package look like the eventual module.

from datetime._datetime import MINYEAR, MAXYEAR
from datetime._datetime import timedelta
from datetime._datetime import time, timetz
from datetime._datetime import date, datetime, datetimetz
from datetime._datetime import tzinfo

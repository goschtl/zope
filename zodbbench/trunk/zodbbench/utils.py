############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################

"""Utilities for helping build ZODB benchmarks.

In large part, this consists of wrappers allowing a uniform way to spell
basic operations (like "commit the current transaction") across ZODB
versions.
"""

import sys
import tempfile

import ZODB
from ZODB.FileStorage import FileStorage

__all__ = ['tcommit',    # commit current transaction
           'tabort',     # abort current transaction
           'tcurrent',   # return current transaction

           # `now` is time.clock on Windows, and time.time elsewhere:
           # an approximation to the best-resolution wall-clock timer
           # available.
           'now',        # time.clock on Windows, time.time elsewhere

           # A base class for benchmarks, capturing some common needs.
           'BenchBase',
          ]

# Figure out which version of ZODB is in use.
first_two = map(int, ZODB.__version__.split('.')[:2])
assert len(first_two) == 2

if first_two <= [3, 2]:
    # ZODB 3.2.0 or earlier.

    # `get_transaction` magically appears in __builtin__ as a result of
    # importing ZODB.
    tcurrent = get_transaction

    def tcommit():
        get_transaction().commit()

    def tabort():
        get_transaction().abort()

else:
    # ZODB 3.3.0 or later.
    import transaction
    tcurrent = transaction.get
    tcommit = transaction.commit
    tabort = transaction.abort

    del transaction

del first_two

if sys.platform == "win32":
    from time import clock as now
else:
    from time import time as now

class BenchBase(object):
    name = None   # subclass should override with benchmark name

    def open_fs(self, path=None):
        """Open a FileStorage.

        If `path` is None (the default), a new FileStorage is created
        in a temp directory.

        These attributes are set on `self`:

            path      path to the .fs file
            storage   the FileStorage instance
            db        DB(storage)
            conn      db.open(), a connection to the FileStorage
        """

        if path is None:
            self.path = tempfile.mktemp(suffix=".fs")
        else:
            self.path = path
        self.storage = FileStorage(self.path)
        self.db = ZODB.DB(self.storage)
        self.conn = self.db.open()

    def close_and_delete(self):
        "Close self.db and delete files associated with the storage."""

        self.db.close()

        # Storage .cleanup methods delete all files associated with a
        # storage (like .fs, .index, .lock, etc).  They generally don't
        # exist before ZODB 3.2, though.
        self.storage.cleanup()


    def report(self, msg):
        """Display a report to stdout.

        The starts by listing the name of the benchmark (self.name),
        then gives the Python and ZODB versions in use, and then displays
        `msg`.
        """

        print "Benchmark", self.name
        print "Python version:", sys.version
        print "ZODB version:", ZODB.__version__
        print msg

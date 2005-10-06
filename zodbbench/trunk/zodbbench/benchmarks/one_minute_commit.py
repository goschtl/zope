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

"""How many commits can we finish in one minute?

This starts with an empty database and an empty IIBTree t.  Then it does:

    i = 0
    while less than a minute has passed:
        t[i] = i
        commit
        i += 1

and reports on how many commits it completed in one minute.
"""

from BTrees.IIBTree import IIBTree

from zodbbench.utils import now, tcommit, BenchBase

class OneMinute(BenchBase):
    name = "one-minute commit"

    def __init__(self):
        self.open_fs()

    def drive(self):
        try:
            t = self.conn.root()['tree'] = IIBTree()
            i = 0
            start = now()
            deadline = start + 60 # one minute
            while now() < deadline:
                t[i] = i
                tcommit()
                i += 1
            self.elapsed = now() - start
            self.ntransactions = i
        finally:
            self.close_and_delete()

    def report(self):
        msg = "Did %d commits in %.1f seconds, for %.2f txn/sec." % (
                self.ntransactions,
                self.elapsed,
                self.ntransactions / self.elapsed)
        BenchBase.report(self, msg)

def main():
    om = OneMinute()
    om.drive()
    om.report()

if __name__ == "__main__":
    main()

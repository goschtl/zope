##############################################################################
#
# Copyright (c) 2007-2008 Zope Foundation and contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""ZEORaid online recovery implementation."""


class Recovery(object):
    """ZEORaid online recovery implementation.
    """

    _current = 0
    raid_transaction_count = 0
    target_transaction_count = 0

    def __init__(self, raid_storage, target_name):
        self.raid_storage = raid_storage
        self.target_name = target_name
        self.target = raid_storage.storages[target_name]
        self.target_transaction_count = ...
        # initialize counting up self.raid_transaction_count

    # transaction_log(offset, length) -> [undo_info, ...]
    # transaction_details(tid) -> [oid, ...]

    def get_raid_transaction_info(self, n):
        """Retrieves the n-th transaction info from the RAID, counting from
        the beginning of the storage's history.
        """

    def get_target_transaction_info(self, n):
        """Retrieves the n-th transaction info from the target storage,
        counting from the beginning of the storage's history.
        """

    def __call__(self):
        """Performs recovery."""
        # Verify old transactions that may already be stored in the target
        # storage.
        for self._current in xrange(self.target_transaction_count):
            if (self.get_raid_transaction_info(self._current) !=
                self.get_target_transaction_info(self._current)):
                raise XXX

        # Recover all transaction from that point on until self._current
        # equals self.raid_transaction_count.
        # self._current now points to the first transaction to be copied.
        # We need to do a "while True" loop in order to be able to check on
        # our progress and finalize recovery atomically.
        while True:
            commit lock
            try:
                if self._current == self.raid_transaction_count:
                    no longer degraded
                    break
            finally:
                commit unlock

            # Recover transaction self._current.
            foo

            self._current += 1

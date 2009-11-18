##############################################################################
#
# Copyright (c) Zope Corporation.  All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

import zc.bsddbstorage

class Storage:

    def __init__(self, config):
        self.config = config
        self.name = config.getSectionName()

    def open(self):
        config = self.config
        return zc.bsddbstorage.Storage(
            config.path,
            config.blob_dir,
            pack=config.pack,
            create=config.create,
            read_only = config.read_only,
            detect_deadlocks = config.detect_deadlocks,
            remove_logs = config.remove_logs,
            checkpoint = config.checkpoint,
            autopack = config.autopack,
            )

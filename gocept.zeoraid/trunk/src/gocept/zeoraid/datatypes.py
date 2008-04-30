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
"""ZConfig storage type definitions.
"""

import ZODB.config
import gocept.zeoraid.storage


class Storage(ZODB.config.BaseConfig):

    def open(self):
        return gocept.zeoraid.storage.RAIDStorage(
            self.name,
            self.config.storages,
            blob_dir=self.config.blob_dir,
            read_only=self.config.read_only,
            shared_blob_dir=self.config.shared_blob_dir)

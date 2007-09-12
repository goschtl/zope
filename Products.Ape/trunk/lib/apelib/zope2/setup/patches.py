##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Monkey-patches necessary to make apelib work in Zope.

$Id$
"""

from Acquisition import aq_base

from apelib.zodb3.utils import zodb_copy


def apply_copy_support_patch():
    # Fall back to copying by pickle when ZEXP export/import is not
    # implemented.
    def _getCopy(self, container):
        try:
            return self._real_getCopy(container)
        except NotImplementedError:
            return zodb_copy(aq_base(self))

    from OFS.CopySupport import CopySource
    if not hasattr(CopySource, '_real_getCopy'):
        CopySource._real_getCopy = CopySource._getCopy
        CopySource._getCopy = _getCopy


def apply_patches():
    apply_copy_support_patch()

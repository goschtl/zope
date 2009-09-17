#############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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

import megrok.layout

import Acquisition


class Layout(megrok.layout.Layout, Acquisition.Explicit):

    def __init__(self, *args):
        super(Layout, self).__init__(*args)
        if not (self.static is None):
            # static should be wrapper correctly with acquisition,
            # otherwise you will not be able to compute URL for
            # resources.
            self.static = self.static.__of__(self)

    # We let getPhysicalPath to be acquired. This make static URL's
    # work, and prevent us to inherit from Acquisition.Implicit
    getPhysicalPath = Acquisition.Acquired


class Page(megrok.layout.Page, Acquisition.Explicit):

    def __init__(self, *args):
        super(Page, self).__init__(*args)
        if not (self.static is None):
            # static should be wrapper correctly with acquisition,
            # otherwise you will not be able to compute URL for
            # resources.
            self.static = self.static.__of__(self)

    # We let getPhysicalPath to be acquired. This make static URL's
    # work, and prevent us to inherit from Acquisition.Implicit
    getPhysicalPath = Acquisition.Acquired





##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
from zope.app.publisher.browser.viewmeta import page
from z3c.optionstorage.browser import OptionStorageView

class optionStorage(object):

    def __init__(self, _context, class_=None, **kwargs):
        self._context = _context
        self.class_ = class_
        self.opts = kwargs.copy()
        self.dictlist = []

    def options(self, _context, name, topic):
        self.dictlist.append((name, topic))

    def __call__(self):
        class_ = self.class_
        if class_ is None:
            class_ = OptionStorageView
        class_ = type("OptionStorageView", (class_,),
                      {"dictlist": self.dictlist})
        page(self._context, class_=class_, **self.opts)
        return ()

##############################################################################
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
""" 

$Id:  2007-12-12 12:27:02Z fafhrd $
"""
from interfaces import IFormWrapper


class FormView(object):

    def isWrapped(self):
        context = self.context.__parent__

        while 1:
            if IFormWrapper.providedBy(context):
                return True

            context = getattr(context, '__parent__', None)
            if context is None:
                return False

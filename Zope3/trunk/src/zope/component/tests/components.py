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
"""

$Id: components.py,v 1.2 2002/12/25 14:13:32 jim Exp $
"""
__metaclass__ = type # All classes are new style when run with Python 2.2+

from zope.interface import Interface
from zope.interface import Attribute

class IApp(Interface):
    a = Attribute('test attribute')
    def f(): "test func"

class IContent(Interface): pass

class Content: __implements__ = IContent

class Comp:
    __used_for__ = IContent
    __implements__ = IApp

    a=1
    def f(): pass

comp = Comp()

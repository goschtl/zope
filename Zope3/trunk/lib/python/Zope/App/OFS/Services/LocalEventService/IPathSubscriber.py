##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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

Revision information:
$Id: IPathSubscriber.py,v 1.2 2002/06/10 23:28:10 jim Exp $
"""
from Interface.Attribute import Attribute
from Zope.Event.ISubscriber import IIndirectSubscriber


class IPathSubscriber(IIndirectSubscriber):
    
    def __init__(wrapped_subscriber):
        """creates new PathSubscriber for the given wrapped_subscriber"""
    
    subscriber_path = Attribute(
        """the slash-delineated absolute url to the subscriber"""
        )
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
$Id: IPathSubscriber.py,v 1.4 2002/11/11 08:38:36 stevea Exp $
"""
from Interface.Attribute import Attribute
from Zope.Event.ISubscriber import IIndirectSubscriber

class IPathSubscriber(IIndirectSubscriber):
    
    def __init__(wrapped_subscriber):
        """creates new PathSubscriber for the given wrapped_subscriber"""
    
    subscriber_path = Attribute(
        """the slash-delineated physical path to the subscriber"""
        )

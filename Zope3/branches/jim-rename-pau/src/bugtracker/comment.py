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
"""A simple Comment

$Id: comment.py,v 1.1 2003/07/24 18:08:03 srichter Exp $
"""
from persistent import Persistent

from zope.interface import implements

from zope.app.container.contained import Contained

from bugtracker.interfaces import IComment
from bugtracker.interfaces import IBugContained
from bugtracker.renderable import RenderableText


class Comment(Persistent, Contained):

    implements(IComment, IBugContained)

    # See zopeproducts.bugtracker.interfaces.IComment
    body = RenderableText('')

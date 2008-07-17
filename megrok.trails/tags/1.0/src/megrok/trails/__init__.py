##############################################################################
#
# Copyright (c) 2007-2008 Zope Corporation and Contributors.
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

"""megrok.trails - automatic URL traversal for Grok

The TrailHead and Trail components provided in this module allow a
developer to write recipes, called 'trails', for the kinds of URLs which
he wants his web application to accept.  See README.txt for more details.

"""
from megrok.trails.components import TrailHead, Trail

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
"""Dependency Framework

  Problem 

    Objects sometimes depend on other objects without the cooperation
    of the objects being depended upon.  For example, service
    directives depend on services. It is important to avoid deleting
    services if there are dependent service directives. We want to
    avoid adding dependency checks to every service implementation,

  Proposal

    A generic dependecy framework is proposed.   Objects that are
    depended on should implement IDependable.

$Id: __init__.py,v 1.1 2002/10/14 11:51:05 jim Exp $
"""
__metaclass__ = type

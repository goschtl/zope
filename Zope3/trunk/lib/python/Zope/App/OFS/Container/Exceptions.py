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
"""Define adder component for folders.

$Id: Exceptions.py,v 1.3 2002/12/20 22:19:28 jeremy Exp $
"""

class DuplicateIDError(KeyError):
    pass

class ContainerError(Exception):
    """An error of a container with one of its components."""
    
class UnaddableError(ContainerError):
    """An object cannot be added to a container."""
    
    def __init__(self, container, obj, message=""):
        self.container = container
        self.obj = obj
        self.message = message and ": %s" % message
    
    def __str__(self):
        return ("%(obj)s cannot be added "
                "to %(container)s%(message)s" % self.__dict__)

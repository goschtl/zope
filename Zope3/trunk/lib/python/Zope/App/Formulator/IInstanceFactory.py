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

$Id: IInstanceFactory.py,v 1.2 2002/06/10 23:27:46 jim Exp $
"""

from Zope.ComponentArchitecture.IContextDependent import IContextDependent

class IInstanceFactory(IContextDependent):
    """
    If the Instance Factory is implemented by an object, then this object
    can be used as factory for other components, such as Views.
    """

    def realize(context):
        """
        Relaizes an instance in a particular context/evironment. This
        method basically replaces __init__(context) for class-based
        factories.
        """


    def __call__(context):
        """
        Basically calls realize(context). However it must be implemented
        too, so that the factory is callable This method has to return the
        produced object.
        """

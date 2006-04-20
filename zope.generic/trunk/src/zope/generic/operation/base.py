##############################################################################
#
# Copyright (c) 2005, 2006 Zope Corporation and Contributors.
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
$Id$
"""

__docformat__ = 'restructuredtext'

from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

from zope.generic.keyface import IAttributeKeyfaced
from zope.generic.component.api import Keyface

from zope.generic.operation import IOperation
from zope.generic.operation import IPrivateOperation



class Operation(Keyface):
    """Generic operation wrapper."""

    implements(IOperation)

    keyface = FieldProperty(IAttributeKeyfaced['__keyface__'])

    def __init__(self, callable=None, keyface=None):
        self.__callable = callable

        # otherwise use IPrivatConfigurationHandler
        if keyface is not None:
            self.__keyface__ = keyface
        else:
            self.__keyface__ = IPrivateOperation

    def __call__(self, context, *pos, **kws):
        self._proceed(context)

    def _proceed(self, context, *pos, **kws):
        # this method can be overwritten by subclasses
        if self.__callable is not None:
            self.__callable(context, *pos, **kws)



class OperationChain(Operation):
    """Generic operation chain wrapper."""

    def __init__(self, operations, keyface=None):
        super(OperationChain, self).__init__(None, keyface)
        self.__operations = operations

    def _proceed(self, context, *pos, **kws):
        """Invoke operation in the listed order."""
        [operation(context) for operation in self.__operations]

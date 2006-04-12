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

from zope.generic.operation import IOperation
from zope.generic.operation import IPrivateOperation



class Operation(object):
    """Generic operation wrapper."""

    implements(IOperation)

    interface = FieldProperty(IOperation['interface'])

    def __init__(self, callable=None, interface=None):
        self.__callable = callable

        # otherwise use IPrivatConfigurationHandler
        if interface is not None:
            self.interface = interface
        else:
            self.interface = IPrivateOperation

    def __call__(self, context, *pos, **kws):
        self._proceed(context)

    def _proceed(self, context, *pos, **kws):
        # this method can be overwritten by subclasses
        if self.__callable is not None:
            self.__callable(context, *pos, **kws)



class OperationChain(Operation):
    """Generic operation chain wrapper."""

    def __init__(self, operations, interface=None):
        super(OperationChain, self).__init__(None, interface)
        self.__operations = operations

    def _proceed(self, context, *pos, **kws):
        """Invoke operation in the listed order."""
        [operation(context) for operation in self.__operations]

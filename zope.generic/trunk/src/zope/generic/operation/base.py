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
from zope.generic.keyface.api import Keyface
from zope.generic.configuration.api import parameterToConfiguration

from zope.generic.operation import IOperation
from zope.generic.operation import IPrivateOperation



class Operation(Keyface):
    """Generic operation wrapper."""

    implements(IOperation)

    __keyface__ = FieldProperty(IAttributeKeyfaced['__keyface__'])

    def __init__(self, callable=None, keyface=None, input=None, output=None):
        self._callable = callable
        self._input = input
        self._output = output

        # otherwise use IPrivatConfigurationHandler
        if keyface is not None:
            self.__keyface__ = keyface
        else:
            self.__keyface__ = IPrivateOperation

    def __call__(self, context, *pos, **kws):
        # this method can be overwritten by subclasses
        if self._callable is not None:
            return self._callable(context, *pos, **kws)



class OperationPipe(Operation):
    """Generic operation chain wrapper."""

    def __init__(self, operations, keyface=None, input=None, output=None):
        super(OperationPipe, self).__init__(None, keyface, input, output)
        self._operations = operations

    def __call__(self, context, *pos, **kws):
        """Invoke operation in the listed order."""
        last_output = parameterToConfiguration(self._input, *pos, **kws)
        for operation in self._operations:
            if last_output is not None:
                last_output = operation(context, last_output)

            else:
                last_output = operation(context)

        return last_output

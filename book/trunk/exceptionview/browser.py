##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Exception-raising View

$Id$
"""
from book.exceptionview.interfaces import PaymentException

class PaymentExceptionView(object):
    """This is a view for `IPaymentException` exceptions."""

    def __call__(self, *args, **kw):
        self.request.response.setStatus(402)
        return self.index(*args, **kw)


class RaiseExceptionView(object):
    """The view that raises the exception"""

    def raisePaymentException(self):
        raise PaymentException, 'You are required to pay.'

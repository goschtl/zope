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
try:
    from Interface import Interface
except ImportError:
    class Interface: pass

class ITransaction(Interface):
    """Transaction objects

    Application code typically gets these by calling
    get_transaction().
    """

    def abort(subtransaction=0):
        """Abort the current transaction

        If subtransaction is true, then only abort the current subtransaction.
        """

    def begin(info=None, subtransaction=0):
        """Begin a transaction

        If info is specified, it must be a string and will be used to
        initialize the transaction description.

        If subtransaction is true, then begin subtransaction.
        """

    def commit(subtransaction=0):
        """Commit a transaction

        If subtransaction is true, then only abort the current subtransaction.
        """

    def register(object):
        """Register the object with the current transaction.

        The object may have a '_p_jar' attribute. If it has this
        attribute then the attribute value may be 'None', or an object
        that implements the IDataManager interface. If the value is
        'None', then the object will not affect the current
        transaction.

        If the object doesn't have a '_p_jar' attribute, then the
        object must implement the IDataManager interface itself.
        """

    def note(text):
        """Add the text to the transaction description

        If there previous description isn't empty, a blank line is
        added before the new text.
        """

    def setUser(user_name, path="/"):
        """Set the transaction user name.

        The user is actually set to the path followed by a space and
        the user name.
        """

    def setExtendedInfo(name, value):
        """Set extended information
        """

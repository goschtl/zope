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

$Id: IUsernamePassword.py,v 1.2 2002/06/10 23:29:37 jim Exp $
"""

from Interface import Interface

# XXX These interfaces should be located in a more central location.
# (so I don't mind putting them together in one module for now ;-) )


class ICredentials(Interface):
    """Base interface for presentation of authentication credentials.

    Different kinds of credentials include username/password, client
    certificate, IP address and port, etc., including combinations.
    """


class IUsernamePassword(ICredentials):
    """A type of authentication credentials consisting of user name and
    password.  The most recognized form of credentials.
    """

    def getUserName():
        """Returns the user name presented for authentication.
        """

    def getPassword():
        """Returns the password presented for authentication.
        """


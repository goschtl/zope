##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""'format' TALES Namespace Interfaces

$Id: interfaces.py,v 1.1 2003/09/16 22:18:56 srichter Exp $
"""
from zope.interface import Interface


class IFormatTalesAPI(Interface):

    def shortDate(self):
        """Returns the short date using the user's locale.

        The context of this namespace must be a datetime object, otherwise an
        exception is raised.
        """

    def mediumDate(self):
        """Returns the medium date using the user's locale.

        The context of this namespace must be a datetime object, otherwise an
        exception is raised.
        """
        
    def longDate(self):
        """Returns the long date using the user's locale.

        The context of this namespace must be a datetime object, otherwise an
        exception is raised.
        """

    def fullDate(self):
        """Returns the full date using the user's locale.

        The context of this namespace must be a datetime object, otherwise an
        exception is raised.
        """

    def shortTime(self):
        """Returns the short time using the user's locale.

        The context of this namespace must be a datetime object, otherwise an
        exception is raised.
        """

    def mediumTime(self):
        """Returns the medium time using the user's locale.

        The context of this namespace must be a datetime object, otherwise an
        exception is raised.
        """

    def longTime(self):
        """Returns the long time using the user's locale.

        The context of this namespace must be a datetime object, otherwise an
        exception is raised.
        """

    def fullTime(self):
        """Returns the full time using the user's locale.

        The context of this namespace must be a datetime object, otherwise an
        exception is raised.
        """

    def shortDateTime(self):
        """Returns the short datetime using the user's locale.

        The context of this namespace must be a datetime object, otherwise an
        exception is raised.
        """

    def mediumDateTime(self):
        """Returns the  datetime using the user's locale.

        The context of this namespace must be a datetime object, otherwise an
        exception is raised.
        """

    def longDateTime(self):
        """Returns the long datetime using the user's locale.

        The context of this namespace must be a datetime object, otherwise an
        exception is raised.
        """

    def fullDateTime(self):
        """Returns the full datetime using the user's locale.

        The context of this namespace must be a datetime object, otherwise an
        exception is raised.
        """

    def decimal(self):
        """Returns the full datetime using the user's locale.

        The context of this namespace must be a datetime object, otherwise an
        exception is raised.
        """

    def percent(self):
        """Returns the floating point as percentage using the user's locale.

        The context of this namespace must be a floating point object,
        otherwise an exception is raised.
        """

    def scientific(self):
        """Returns the floating point in scientific notation using the user's
        locale.

        The context of this namespace must be a floating point object,
        otherwise an exception is raised.
        """

    def currency(self):
        """Returns the floating point as currency using the user's locale.

        The context of this namespace must be a floating point object,
        otherwise an exception is raised.
        """

    

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
"""SMTP service.

$Id: ISMTPService.py
"""
from Interface import Interface


class ISMTPService(Interface):
    """TTW manageable SMTP service
    """

    def sendMessage(messageText, mto=None, mfrom=None, subject=None, encode=None):         
        """Send mail from a formatted message

        The message text is message in RFC 822 format. The method will make sure that
        the message as a subject.
        """

    def sendBody(mto, mfrom, subject, body, encode=None):
        """Send mail from a formatted message

        The body text is message in RFC 822 format. The method will work without
        checking subject. 
        """

##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Fake Mailer that just prints.
"""

import email
import sys

import zope.interface
import zope.sendmail.interfaces

class Mailer:

    zope.interface.implements(zope.sendmail.interfaces.IMailer)

    def send(self, fromaddr, toaddrs, message_string):
        message = email.message_from_string(message_string)
        print >> sys.stderr, 'From', fromaddr
        print >> sys.stderr,  'To', toaddrs
        print >> sys.stderr,  '-'*70
        for h in message.keys():
            for v in message.get_all(h):
                print >> sys.stderr,  "%s: %s" % (h, v)
            
        print >> sys.stderr,  message.get_payload(decode=True)
        print >> sys.stderr,  '-'*70

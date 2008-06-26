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
import email.Header
import sys

import zope.interface
import zope.sendmail.interfaces

class Mailer:

    zope.interface.implements(zope.sendmail.interfaces.IMailer)

    def send(self, fromaddr, toaddrs, message_string):
        message = email.message_from_string(message_string)
        print '='*70
        print 'From', fromaddr
        print 'To', toaddrs
        print '-'*70
        for h in message.keys():
            for v in message.get_all(h):
                # we want to decode encoded headers, showing the encoding.
                # we also want to simplify the display, both for backwards
                # compatibility and for ease of reading in tests
                decoded = []
                raw = email.Header.decode_header(v)
                if isinstance(raw, tuple):
                    raw = [raw]
                for info in raw:
                    if info[1] is None:
                        decoded.append(info[0])
                    else:
                        decoded.append(info)
                if len(decoded) == 1:
                    decoded = decoded[0]
                print "%s: %s" % (h, decoded)
        if message.is_multipart():
            # show each part
            for m in message.get_payload():
                print '.'*70
                print 'Content-Type:', m.get_content_type()
                print m.get_payload(decode=True)
        else:
            print message.get_payload(decode=True)
        print '='*70
        sys.stdout.flush()

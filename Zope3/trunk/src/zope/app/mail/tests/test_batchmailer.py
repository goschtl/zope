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
"""MailService Implementation

Simple implementation of the MailService, Mailers and MailEvents.

$Id: test_batchmailer.py,v 1.2 2003/05/01 19:35:24 faassen Exp $
"""
from unittest import TestSuite, makeSuite
from test_simplemailer import TestSimpleMailer


class TestBatchMailer(TestSimpleMailer):
    # Minimal test.
    pass


def test_suite():
    return TestSuite((
        makeSuite(TestBatchMailer),
        ))

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
"""Helper functions for dealing with URLs."""

__docformat__ = "reStructuredText"

import posixpath
import urllib


def file_url(path):
    urlpart = urllib.pathname2url(path)
    if urlpart.startswith("///"):
        urlpart = urlpart[2:]
    urlpart = posixpath.normpath(urlpart)
    return "file://" + urlpart

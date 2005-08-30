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
    return "file://" + pathname2url(path)

def pathname2url(path):
    urlpart = urllib.pathname2url(path)
    # On Windows, pathname2url() returns too many slashes, or it
    # returns too few on Unix.  This makes everything conform to the
    # expectations for Unix.
    if urlpart.startswith("///"):
        urlpart = urlpart[2:]
    return posixpath.normpath(urlpart)

##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Tools to deal with the mapping of resources to CVS URLs."""

import os.path
import posixpath
import urllib2
import urlparse

from zpkgtools import cvsloader


class CvsMapLoadingError(ValueError):
    def __init__(self, message, lineno):
        self.lineno = lineno
        ValueError.__init__(self, message)


def load(f, base=None, mapping=None):
    cvsbase = None
    if base is not None:
        try:
            cvsbase = cvsloader.parse(base)
        except ValueError:
            pass
    if mapping is None:
        mapping = {}
    lineno = 0
    for line in f:
        lineno += 1
        line = line.strip()
        if line[:1] in ("", "#"):
            continue

        parts = line.split()
        if len(parts) != 2:
            raise CvsMapLoadingError("malformed package specification",
                                     lineno)
        resource, url = parts
        try:
            cvsurl = cvsloader.parse(url)
        except ValueError:
            # conventional URL
            if base is not None:
                url = urlparse.urljoin(base, url)
        else:
            if isinstance(cvsurl, cvsloader.RepositoryUrl):
                if cvsbase is None:
                    raise CvsMapLoadingError(
                        "repository: URLs are not supported"
                        " without a cvs: base URL",
                        lineno)
                cvsurl = cvsurl.join(cvsbase)
            url = cvsurl.getUrl()

        # We only want to add it once, so that loading several
        # mappings causes the first defining a resource to "win":
        if resource not in mapping:
            mapping[resource] = url
        # else tell the user of the conflict?

    return mapping


def fromPathOrUrl(path, mapping=None):
    if os.path.isfile(path):
        # prefer a cvs: URL over a local path if possible:
        try:
            cvsurl = cvsloader.fromPath(path)
        except IOError, e:
            print "IOError:", e
            base = os.path.dirname(path)
        else:
            cvsurl.path = posixpath.dirname(cvsurl.path)
            base = cvsurl.getUrl()
        f = open(path, "rU")
    else:
        f = urllib2.urlopen(path)
    try:
        mapping = load(f, base, mapping)
    finally:
        f.close()
    return mapping

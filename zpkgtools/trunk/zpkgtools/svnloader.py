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
"""Subversion support functions."""

import os
import posixpath
import sys
import urllib
import urlparse

from zpkgtools import Error


class SubversionLoadingError(Error):
    """Raised when there was some error loading from Subversion.

    :Ivariables:
      - `url`: Subversion URL.
      - `exitcode`: Return code of the Subversion process.
    """

    def __init__(self, url, exitcode):
        self.url = cvsurl
        self.exitcode = exitcode
        Error.__init__(self, ("could not load from %s (svn exit code %d)"
                              % (url, exitcode)))


if sys.platform[:3].lower() == "win":
    ROOTDIR = "\\"
else:
    ROOTDIR = "/"


def is_subversion_url(url):
    """Return `True` if the URL should be used for Subversion."""
    type, rest = urllib.splittype(url)
    if type in ("svn", "svn+ssh"):
        return True
    if type == "file":
        if not url.startswith("file://"):
            return False
        parts = urlparse.urlsplit(url)
        if not parts[1] in ("", "localhost"):
            return False
        path = urllib.url2pathname(parts[2])
        # need to look for a subversion repository along the path
        while path and path != ROOTDIR and not os.path.exists(path):
            path = os.path.dirname(path)
        # path exists; is there a Subversion repository there?
        if is_repository(path):
            return True
        path = os.path.dirname(path)
        if is_repository(path):
            return True
        path = os.path.dirname(path)
        if is_repository(path):
            return True
    # We just don't handle http: and https: repositories, and I've no
    # idea how to detect them yet.
    return False


REPOSITORY_CONTENT = [
    # name, isdir
    ("conf", True),
    ("dav", True),
    (os.path.join("db", "DB_CONFIG"), False),
    ("hooks", True),
    ("locks", True),
    ]

def is_repository(path):
    # internal use
    """Return true if `path` is a Subversion repository.

    This uses some general expectations of what the repository is
    supposed to look like; some repositories may not have everything
    this looks for, but that's pretty unlikely.
    """
    if not os.path.isdir(path):
        return False
    for name, isdir in REPOSITORY_CONTENT:
        fn = os.path.join(path, name)
        if isdir:
            ok = os.path.isdir(fn)
        else:
            ok = os.path.isfile(fn)
        if not ok:
            return False
    return True


class SubversionLoader:
    # This is really only an object so the API mirrors the CvsLoader.
    """Simpler loader object that loads from Subversion."""

    def load(self, url, workdir):
        # do an "svn cat" to get a file, or learn that this is a directory
        stdin, stdout, stderr = os.popen3("svn cat '%s'" % url)
        data = stdout.read()
        if not data:
            # maybe url referenced a directory
            err = stderr.readline()
            if "directory" in err:
                # it is!
                target = os.path.join(workdir, "foo")
                rc = os.system("svn export -q '%s' '%s'" % (url, target))
                if rc != 0:
                    raise SubversionLoadingError(url, rc)
                return target
            else:
                # don't know the exit code, so make one up
                raise SubversionLoadingError(url, 1)
        else:
            name = posixpath.basename(url)
            path = os.path.join(workdir, name)
            f = open(path, "wb")
            f.write(data)
            f.close()
            return path

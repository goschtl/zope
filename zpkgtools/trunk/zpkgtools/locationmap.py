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
"""Tools to deal with the mapping of resources to URLs."""

import logging
import os.path
import posixpath
import sets
import urllib
import urllib2
import urlparse

from zpkgtools import cvsloader
from zpkgtools import loader


_logger = logging.getLogger(__name__)


class MapLoadingError(ValueError):
    def __init__(self, message, filename, lineno):
        self.filename = filename
        self.lineno = lineno
        ValueError.__init__(self, message)

class LocationMap(dict):

    def get(self, name, default=None):
        """Look up an entry froma map

        If an entry isn't found directly, check for a prefix

          >>> map = LocationMap({'foo': 'svn://spam.com/repos/foo'})
          >>> map.get('foo')
          'svn://spam.com/repos/foo'
          >>> map.get('foo.bar')
          'svn://spam.com/repos/foo/bar'
          >>> map.get('foo.bar.baz')
          'svn://spam.com/repos/foo/bar/baz'
          >>> map.get('z')
          >>> map.get('z.x')
          >>> map.get('z.x.y')

        """

        r = dict.get(self, name)
        if r:
            return r
        
        suffix = ''
        while 1:
            l = name.rfind('.')
            if l > 0:
                suffix = '/'+ name[l+1:] + suffix
                name = name[:l]
            else:
                break
            r = dict.get(self, name)
            if r:
                return r + suffix
            
        return default

    __contains__ = get

    def __getitem__(self, name):
        """Look up an entry froma map

        If an entry isn't found directly, check for a prefix

          >>> map = LocationMap({'foo': 'svn://spam.com/repos/foo'})
          >>> map['foo']
          'svn://spam.com/repos/foo'
          >>> map['foo.bar']
          'svn://spam.com/repos/foo/bar'
          >>> map['foo.bar.baz']
          'svn://spam.com/repos/foo/bar/baz'

          >>> map['z']
          Traceback (most recent call last):
          ...
          KeyError: 'z'

          >>> map['z.x']
          Traceback (most recent call last):
          ...
          KeyError: 'z.x'

          >>> map['z.x.y']
          Traceback (most recent call last):
          ...
          KeyError: 'z.x.y'

        """
        r = self.get(name)
        if r:
            return r
        raise KeyError, name

        

def load(f, base=None, mapping=None):
    cvsbase = None
    if base is not None:
        try:
            cvsbase = loader.parse(base)
        except ValueError:
            pass
    if mapping is None:
        mapping = LocationMap()
    local_entries = sets.Set()
    lineno = 0
    for line in f:
        lineno += 1
        line = line.strip()
        if line[:1] in ("", "#"):
            continue

        parts = line.split()
        if len(parts) != 2:
            raise MapLoadingError("malformed package specification",
                                  getattr(f, "name", "<unknown>"), lineno)
        resource, url = parts
        try:
            cvsurl = loader.parse(url)
        except ValueError:
            # conventional URL
            if cvsbase is None:
                url = urlparse.urljoin(base, url)
        else:
            if isinstance(cvsurl, cvsloader.RepositoryUrl):
                if cvsbase is None:
                    raise MapLoadingError(
                        "repository: URLs are not supported"
                        " without a cvs: base URL",
                        getattr(f, "name", "<unknown>"), lineno)
                cvsurl = cvsbase.join(cvsurl)
            url = cvsurl.getUrl()

        # We only want to add it once, so that loading several
        # mappings causes the first defining a resource to "win":
        if resource not in mapping:
            mapping[resource] = url
        elif resource in local_entries:
            _logger.warn(
                "found duplicate entry for resource %r in %s at line %d",
                resource, getattr(f, "name", "<unknown>"), lineno)
        local_entries.add(resource)
        # else tell the user of the conflict?

    return mapping


def fromPathOrUrl(path, mapping=None):
    # XXX need to deal with cvs: URLs directly!
    # still need to support Subversion here
    if os.path.isfile(path):
        # prefer a revision-control URL over a local path if possible:
        rcurl = loader.fromPath(path)
        if rcurl is None:
            base = os.path.dirname(path)
        else:
            base = loader.baseUrl(rcurl)
        f = open(path, "rU")
    else:
        try:
            cvsurl = loader.parse(path)
        except ValueError:
            f = urllib2.urlopen(path, "rU")
        else:
            f = loader.open(path, "rU")
        base = loader.baseUrl(path)
    try:
        return load(f, base, mapping)
    finally:
        f.close()

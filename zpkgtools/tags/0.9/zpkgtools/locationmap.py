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
"""Tools to deal with the mapping of resources to URLs."""

import os.path
import posixpath
import re
import urllib
import urllib2
import urlparse
import UserDict

from zpkgsetup import loggingapi as logging
from zpkgsetup import urlutils

from zpkgtools import cvsloader
from zpkgtools import loader
from zpkgtools import svnloader


_logger = logging.getLogger(__name__)


class MapLoadingError(ValueError):
    def __init__(self, message, filename, lineno=None):
        self.filename = filename
        self.lineno = lineno
        ValueError.__init__(self, message)


class LocationMap(UserDict.UserDict):

    def __init__(self, *args, **kw):
        UserDict.UserDict.__init__(self, *args, **kw)
        self._wildcards = {}

    def __getitem__(self, key):
        if key in self.data:
            v = self.data[key]
            if v is None:
                raise KeyError(key)
            return v
        # might be supported by the wildcards
        v = self._get_from_wildcards(key)
        if v is None:
            raise KeyError(key)
        return v

    def __setitem__(self, key, item):
        self.data[key] = item

    def __delitem__(self, key):
        if key in self.data and self.data[key] != None:
            del self.data[key]
        elif key in self:
            # must be here as a wildcard
            self.data[key] = None
        else:
            raise KeyError(key)

    def get(self, key, default=None):
        if key in self.data:
            v = self.data[key]
            if v is None:
                v = default
            return v
        try:
            return self._get_from_wildcards(key)
        except KeyError:
            return default

    def has_key(self, key):
        if key in self.data:
            return self.data[key] is not None
        else:
            return self._get_from_wildcards(key) is not None

    def update(self, dict=None, **kwargs):
        if dict:
            for key, value in dict.iteritems():
                self.data[key] = value
        if len(kwargs):
            self.update(kwargs)

    def pop(self, key, *args):
        return self.data.pop(key, *args)

    def __contains__(self, key):
        if key in self.data:
            return self.data[key] is not None
        else:
            return self._get_from_wildcards(key) is not None

    def _add_wildcard(self, key, location):
        """Add a location for a wildcarded package."""
        self._wildcards[key] = location

    def _get_from_wildcards(self, key):
        """Return location based on wildcards, or None."""
        prefix = key
        suffix = ""
        while "." in prefix:
            pos = prefix.rfind(".")
            name = prefix[pos+1:]
            prefix = prefix[:pos]
            if suffix:
                suffix = "%s/%s" % (name, suffix)
            else:
                suffix = name
            base = self._wildcards.get(prefix)
            if base:
                # join suffix with the path portion of the base
                try:
                    parsed = loader.parse(base)
                except ValueError:
                    # we should distinguish between URLs and local paths here
                    parts = list(urlparse.urlsplit(base))
                    if parts[2]:
                        parts[2] = posixpath.join(parts[2], suffix)
                    else:
                        parts[2] = posixpath.join("", suffix)
                    return urlparse.urlunsplit(parts)
                else:
                    if isinstance(parsed, cvsloader.CvsUrl):
                        parsed.path = posixpath.join(parsed.path, suffix)
                    else:
                        pathpart = RelativePath(suffix)
                        parsed = parsed.join(pathpart)
                    return get_template_url(parsed)
        return None

    def _have_wildcard(self, key):
        """Return true iff we already have a wildcard for key."""
        return key in self._wildcards

class RelativePath:
    def __init__(self, path):
        self.tag = None
        self.path = path


class MapLoader:

    def __init__(self, base, filename, mapping):
        assert base
        self.base = base
        self.filename = filename
        self.mapping = mapping
        self.local_entries = {}
        try:
            self.cvsbase = loader.parse(base)
        except ValueError:
            self.cvsbase = None

    def add(self, resource, url):
        urlparts = url.split()
        if len(urlparts) != 1:
            raise MapLoadingError("malformed package specification",
                                  self.filename)
        try:
            cvsurl = loader.parse(url)
        except ValueError:
            # conventional URL
            if self.cvsbase is None:
                url = urlparse.urljoin(self.base, url)

        if resource in self.local_entries:
            _logger.warn(
                "found duplicate entry for resource %r in %s at line %d",
                resource, self.filename)
        elif resource.endswith(".*"):
            # Deal with wildcarded resources;
            # need to check if it's already there
            wildcard = resource[:-2]
            if not is_module_name(wildcard):
                raise MapLoadingError("wildcard package name specified, but"
                                      " prefix is not a legal package name: %r"
                                      % wildcard,
                                      self.filename)
            if not self.mapping._have_wildcard(wildcard):
                self.mapping._add_wildcard(wildcard, url)
        elif "*" in resource:
            raise MapLoadingError("invalid wildcard specification: %r"
                                  % resource,
                                  self.filename)
        elif resource not in self.mapping:
            # We only want to add it once, so that loading several
            # mappings causes the first defining a resource to "win":
            self.mapping[resource] = url
        self.local_entries[resource] = resource


def load(f, base, mapping):
    """Parse a location map from an open file.

    :param f:  The open file to read from.

    :param base:  URL corresponding to the open file.

    :param mapping:  Mapping to update.

    This routine is not part of the API for this module; it is
    separated out from the `fromPathOrUrl()` function to make it
    easier to test the map parsing aspect of this module.

    """
    lineno = 0
    filename = getattr(f, "name", "<unknown>")
    maploader = MapLoader(base, filename, mapping)
    for line in f:
        lineno += 1
        line = line.strip()
        if line[:1] in ("", "#"):
            continue

        parts = line.split()
        if len(parts) != 2:
            raise MapLoadingError("malformed package specification",
                                  filename, lineno)
        try:
            maploader.add(*parts)
        except MapLoadingError, e:
            e.lineno = lineno
            raise


def get_template_url(parsed):
    #
    # XXX We need to distinguish between the tag being unspecified at
    # times and the tag being specified at others; the Subversion URL
    # classes get these confused, because the abstract model for the
    # URLs isn't sufficient.  For now, this avoids losing the
    # "templateness" of /tags/*/ in Subversion URLs.
    #
    if isinstance(parsed, svnloader.SubversionUrlBase) and not parsed.tag:
        parsed.tag = "*"
    return parsed.getUrl()


def fromPathOrUrl(path, mapping=None):
    """Load or update a map base on the content of a path or URL.

    :param path:  Path to a file (absolute or relative), or URL.

    :param mapping:  Mapping object to update; if omitted or `None`, a
      new `LocationMap` will be created and returned.

    :return: New or updated location map.

    """
    if os.path.isfile(path):
        # prefer a revision-control URL over a local path if possible:
        # XXX why????  this doesn't make much sense
        base = urlutils.file_url(path)
        f = open(path, "rU")
    else:
        try:
            cvsurl = loader.parse(path)
        except ValueError:
            f = urllib2.urlopen(path, "rU")
        else:
            f = loader.open(path, "rU")
        base = path
    if mapping is None:
        mapping = LocationMap()
    try:
        load(f, base, mapping)
    finally:
        f.close()
    return mapping


_ident = "[a-zA-Z_][a-zA-Z_0-9]*"
_module_match = re.compile(r"%s(\.%s)*$" % (_ident, _ident)).match

def is_module_name(string):
    return _module_match(string) is not None

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

from zpkgtools import cvsloader
from zpkgtools import loader
from zpkgtools import svnloader


_logger = logging.getLogger(__name__)

urlmatch = re.compile(r'[a-zA-Z]+://').match

class MapLoadingError(ValueError):
    def __init__(self, message, filename, lineno):
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
                    pathpart = cvsloader.RepositoryUrl(suffix)
                    parsed = parsed.join(pathpart)
                    return get_template_url(parsed)
        return None

    def _have_wildcard(self, key):
        """Return true iff we already have a wildcard for key."""
        return key in self._wildcards


def load(f, base=None, mapping=None):
    cvsbase = None
    if base is not None:
        try:
            cvsbase = loader.parse(base)
        except ValueError:
            pass
    if mapping is None:
        mapping = LocationMap()
    local_entries = {}
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
                if base is None:
                    base = ''
                    
                if not urlmatch(base):
                    base = ('file://' +
                            urllib.pathname2url(os.path.abspath(base))
                            + '/'
                            )

                url = urlparse.urljoin(base, url)
        else:
            if isinstance(cvsurl, cvsloader.RepositoryUrl):
                if cvsbase is None:
                    raise MapLoadingError(
                        "repository: URLs are not supported"
                        " without a cvs: or Subversion base URL",
                        getattr(f, "name", "<unknown>"), lineno)
                cvsurl = cvsbase.join(cvsurl)
                url = get_template_url(cvsurl)

        if resource in local_entries:
            _logger.warn(
                "found duplicate entry for resource %r in %s at line %d",
                resource, getattr(f, "name", "<unknown>"), lineno)
        elif resource.endswith(".*"):
            # Deal with wildcarded resources;
            # need to check if it's already there
            wildcard = resource[:-2]
            if not is_module_name(wildcard):
                raise MapLoadingError("wildcard package name specified, but"
                                      " prefix is not a legal package name: %r"
                                      % wildcard,
                                      getattr(f, "name", "<unknown>"), lineno)
            if not mapping._have_wildcard(wildcard):
                mapping._add_wildcard(wildcard, url)
        elif "*" in resource:
            raise MapLoadingError("invalid wildcard specification: %r"
                                  % resource,
                                  getattr(f, "name", "<unknown>"), lineno)
        elif resource not in mapping:
            # We only want to add it once, so that loading several
            # mappings causes the first defining a resource to "win":
            mapping[resource] = url
        local_entries[resource] = resource

    return mapping


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


_ident = "[a-zA-Z_][a-zA-Z_0-9]*"
_module_match = re.compile(r"%s(\.%s)*$" % (_ident, _ident)).match

def is_module_name(string):
    return _module_match(string) is not None

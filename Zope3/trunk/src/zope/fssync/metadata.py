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
"""Class to maintain fssync metadata.

The metadata entry for something named /path/base, is kept in a file
/path/@@Zope/Entries.xml.  That file is (an XML pickle for) a dict
containing many entries.  The metadata entry for /path/base is stored
under the key 'base'.  The metadata entry is itself a dict.  An empty
entry is considered non-existent, and will be deleted upon flush.  If
no entries remain, the Entries.xml file will be removed.

$Id: metadata.py,v 1.1 2003/05/12 20:19:38 gvanrossum Exp $
"""

import os
import copy

from os.path import exists, isdir, isfile, split, join, realpath, normcase

from zope.xmlpickle import loads, dumps

class Metadata(object):

    def __init__(self, case_insensitive=None):
        """Constructor.

        The case_insensitive can be passed as an argument for testing;
        by default, it is set by observing the behavior of normcase().
        """
        if case_insensitive is None:
            case_insensitive = (normcase("ABC") == normcase("abc"))
        self.case_insensitive = case_insensitive
        self.cache = {} # Keyed by normcase(dirname(realpath(file)))
        self.originals = {} # Original copy as read from file

    def getnames(self, dir):
        """Return the names of known non-empty metadata entries, sorted."""
        dir = realpath(dir)
        entries = self._getentries(dir)
        names = [name for name, entry in entries.iteritems() if entry]
        names.sort()
        return names

    def getentry(self, file):
        """Return the metadata entry for a given file (or directory).

        Modifying the dict that is returned will cause the changes to
        the metadata to be written out when flush() is called.  If
        there is no metadata entry for the file, return a new empty
        dict, modifications to which will also be flushed.
        """
        file = realpath(file)
        dir, base = split(file)
        entries = self._getentries(dir)
        if base in entries:
            return entries[base]
        if self.case_insensitive:
            # Look for a case-insensitive match -- expensive!
            # XXX There's no test case for this code!
            # XXX What if there are multiple matches?
            nbase = normcase(base)
            for b in entries:
                if normcase(b) == nbase:
                    return entries[b]
        # Create a new entry
        entries[base] = entry = {}
        return entry

    def _getentries(self, dir):
        key = normcase(dir)
        if key in self.cache:
            entries = self.cache[key]
        else:
            efile = join(dir, "@@Zope", "Entries.xml")
            if isfile(efile):
                f = open(efile)
                try:
                    data = f.read()
                finally:
                    f.close()
                self.cache[key] = entries = loads(data)
            else:
                self.cache[key] = entries = {}
            self.originals[key] = copy.deepcopy(entries)
        return entries

    def flush(self):
        errors = []
        for key in self.cache:
            try:
                self.flushkey(key)
            except (IOError, OSError), err:
                errors.append(err)
        if errors:
            if len(errors) == 1:
                raise
            else:
                raise IOError, tuple(errors)

    def flushkey(self, key):
        entries = self.cache[key]
        todelete = [name for name, entry in entries.iteritems() if not entry]
        for name in todelete:
            del entries[name]
        if entries != self.originals[key]:
            zdir = join(key, "@@Zope")
            efile = join(zdir, "Entries.xml")
            if not entries:
                if isfile(efile):
                    os.remove(efile)
                    if exists(zdir):
                        try:
                            os.rmdir(zdir)
                        except os.error:
                            pass
            else:
                data = dumps(entries)
                if not exists(zdir):
                    os.makedirs(zdir)
                f = open(efile, "w")
                try:
                    f.write(data)
                finally:
                    f.close()
            self.originals[key] = copy.deepcopy(entries)

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

$Id: metadata.py,v 1.6 2003/07/25 20:18:48 fdrake Exp $
"""

import os
import copy

from cStringIO import StringIO
from os.path import exists, isdir, isfile, split, join, realpath, normcase
from xml.sax import ContentHandler, parseString
from xml.sax.saxutils import quoteattr

case_insensitive = (normcase("ABC") == normcase("abc"))

class Metadata(object):

    def __init__(self):
        """Constructor."""
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
        if case_insensitive:
            # Look for a case-insensitive match -- expensive!
            # XXX There's no test case for this code!
            nbase = normcase(base)
            matches = [b for b in entries if normcase(b) == nbase]
            if matches:
                if len(matches) > 1:
                    raise KeyError("multiple entries match %r" % nbase)
                return entries[matches[0]]
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
                self.cache[key] = entries = load_entries(data)
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
        # Make a copy containing only the "live" (non-empty) entries
        live = {}
        for name, entry in entries.iteritems():
            if entry:
                live[name] = entry
        if live != self.originals[key]:
            zdir = join(key, "@@Zope")
            efile = join(zdir, "Entries.xml")
            if exists(efile) or live:
                data = dump_entries(live)
                if not exists(zdir):
                    os.makedirs(zdir)
                f = open(efile, "w")
                try:
                    f.write(data)
                finally:
                    f.close()
            self.originals[key] = copy.deepcopy(live)


def dump_entries(entries):
    sio = StringIO()
    sio.write("<?xml version='1.0' encoding='utf-8'?>\n")
    sio.write("<entries>\n")
    names = entries.keys()
    names.sort()
    for name in names:
        entry = entries[name]
        sio.write("  <entry name=")
        sio.write(quoteattr(name).encode('utf-8'))
        for k, v in entry.iteritems():
            if v is None:
                continue
            sio.write("\n         %s=%s"
                      % (k.encode('utf-8'), quoteattr(v).encode('utf-8')))
        sio.write("\n         />\n")
    sio.write("</entries>\n")
    return sio.getvalue()

def load_entries(text):
    ch = EntriesHandler()
    try:
        parseString(text, ch)
    except FoundXMLPickle:
        from zope.xmlpickle import loads
        return loads(text)
    else:
        return ch.entries


class EntriesHandler(ContentHandler):
    def __init__(self):
        self.first = True
        self.stack = []
        self.entries = {}

    def startElement(self, name, attrs):
        if self.first:
            if name == "pickle":
                raise FoundXMLPickle()
            elif name != "entries":
                raise InvalidEntriesFile()
            else:
                self.first = False
        if name == "entry":
            if self.stack[-1] != "entries":
                raise InvalidEntriesFile("illegal element nesting")
            else:
                entryname = attrs.getValue("name")
                entry = {}
                for n in attrs.getNames():
                    if n != "name":
                        entry[n] = attrs.getValue(n)
                self.entries[entryname] = entry
        elif name == "entries":
            if self.stack:
                raise InvalidEntriesFile(
                    "<entries> must be the document element")
        else:
            raise InvalidEntriesFile("unknown element <%s>" % name)
        self.stack.append(name)

    def endElement(self, name):
        old = self.stack.pop()
        assert name == old, "%r != %r" % (name, old)

    def characters(self, data):
        if data.strip():
            raise InvalidEntriesFile(
                "arbitrary character data not supported: %r" % data.strip())


class FoundXMLPickle(Exception):
    """Raised by EntriesHandler when the document appears to be an XML
    pickle."""

class InvalidEntriesFile(Exception):
    """Raised by EntriesHandler when the document has an unsupposed
    document element."""

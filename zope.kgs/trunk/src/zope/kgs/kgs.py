##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""KGS configuration file parser."""
import datetime
import dateutil.parser
import os.path
import urllib2
import ConfigParser
from zc.buildout.buildout import _update, _isurl

MAIN_SECTION = 'KGS'
EXTENDS_OPTION = 'extends'

def _open(base, filename, seen):
    """Open a configuration file and return the result as a dictionary,

    Recursively open other files based on options found.

    Note: Shamelessly copied from zc.buildout!
    """

    if _isurl(filename):
        fp = urllib2.urlopen(filename)
        base = filename[:filename.rfind('/')]
    elif _isurl(base):
        if os.path.isabs(filename):
            fp = open(filename)
            base = os.path.dirname(filename)
        else:
            filename = base + '/' + filename
            fp = urllib2.urlopen(filename)
            base = filename[:filename.rfind('/')]
    else:
        filename = os.path.join(base, filename)
        fp = open(filename)
        base = os.path.dirname(filename)

    if filename in seen:
        raise ValueError("Recursive file include", seen, filename)

    seen.append(filename)

    result = {}

    parser = ConfigParser.RawConfigParser()
    parser.optionxform = lambda s: s
    parser.readfp(fp)
    extends = None
    for section in parser.sections():
        options = dict(parser.items(section))
        if section == MAIN_SECTION:
            extends = options.pop(EXTENDS_OPTION, extends)
        result[section] = options

    if extends:
        extends = extends.split()
        extends.reverse()
        for fname in extends:
            result = _update(_open(base, fname, seen), result)

    seen.pop()
    return result

def _getAbsolutePath(section, basePath, name, default):
    path = section.get(name, default)
    if path:
        if not os.path.isabs(path):
            path = os.path.join(basePath, path)
        if path and not os.path.exists(path):
            path = None
    return path


class Package(object):

    def __init__(self, name, versions, tested, testExtras):
        self.name = name
        self.versions = versions
        self.tested = tested
        self.testExtras = testExtras

    def __repr__(self):
        return '<%s %r>' %(self.__class__.__name__, self.name)


class KGS(object):

    name = u'noname'
    version = u'unknown'
    date = None
    changelog = None
    announcement = None
    files = ()
    packages = ()

    def __init__(self, path):
        self.path = path
        self._extract()

    def _extract(self):
        basePath = os.path.dirname(self.path)
        result = _open(basePath, self.path, [])
        if MAIN_SECTION in result:
            section = result[MAIN_SECTION]
            # Get name and version.
            self.name = section.get('name', self.name)
            self.version = section.get('version', self.version)
            # Get the changelog.
            self.changelog = _getAbsolutePath(
                section, basePath, 'changelog', self.changelog)
            # Get the announcement.
            self.announcement = _getAbsolutePath(
                section, basePath, 'announcement', self.announcement)
            # Get the date.
            dateStr = section.get('date')
            if dateStr:
                self.date = dateutil.parser.parse(dateStr).date()
            # Get the release files.
            files = section.get('files')
            if files:
                files = files.split()
                for path in files:
                    if not os.path.isabs(path):
                        path = os.path.join(basePath, path)
                        if path and os.path.exists(path):
                            self.files += (path,)
            del result[MAIN_SECTION]
        self.packages = []
        sections = result.keys()
        sections.sort()
        for section in sections:
            self.packages.append(
                Package(section,
                        result[section]['versions'].split(),
                        ConfigParser.ConfigParser._boolean_states[
                            result[section]['tested']],
                        result[section].get('test-extras')
                        )
                )

    def __repr__(self):
        return '<%s %r>' %(self.__class__.__name__, self.name)


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


class Package(object):

    def __init__(self, name, versions, tested):
        self.name = name
        self.versions = versions
        self.tested = tested

    def __repr__(self):
        return '<%s %r>' %(self.__class__.__name__, self.name)


class KGS(object):

    name = u''
    packages = ()

    def __init__(self, path):
        self.path = path
        self._extract()

    def _extract(self):
        result = _open(os.path.dirname(self.path), self.path, [])
        if MAIN_SECTION in result:
            self.name = result[MAIN_SECTION].get('name', u'')
            del result[MAIN_SECTION]
        self.packages = []
        sections = result.keys()
        sections.sort()
        for section in sections:
            self.packages.append(
                Package(section,
                        result[section]['versions'].split(),
                        ConfigParser.ConfigParser._boolean_states[
                            result[section]['tested']]
                        )
                )

    def __repr__(self):
        return '<%s %r>' %(self.__class__.__name__, self.name)


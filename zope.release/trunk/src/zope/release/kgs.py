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
import ConfigParser

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
        config = ConfigParser.RawConfigParser()
        config.read(self.path)
        if config.has_section('KGS'):
            self.name = config.get('KGS', 'name')
            config.remove_section('KGS')
        self.packages = []
        sections = config.sections()
        sections.sort()
        for section in sections:
            self.packages.append(
                Package(section,
                        config.get(section, 'versions').split(),
                        config.getboolean(section, 'tested')
                        )
                )

    def __repr__(self):
        return '<%s %r>' %(self.__class__.__name__, self.name)


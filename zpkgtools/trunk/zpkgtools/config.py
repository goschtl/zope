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
"""Configuration support for zpkg.

The syntax of the configuration files is incredibly simple, but is
intended to be a strict subset of the ZConfig.  This allows us to
switch to ZConfig in the future if we decide the dependency is worth
it.
"""

import os
import urllib

from zpkgtools import cfgparser
from zpkgtools import locationmap


def non_empty_string(string):
    if not string:
        raise ValueError("value cannot be empty")
    return string

SCHEMA = cfgparser.Schema(
    ({"repository-map": non_empty_string}, [], None),
    )


class Configuration:
    """Configuration settings for zpkg."""

    def __init__(self):
        self.location_maps = []
        self.locations = None

    def finalize(self):
        for loc in self.location_maps:
            self.locations = locationmap.fromPathOrUrl(loc,
                                                       mapping=self.locations)
        if self.locations is None:
            self.locations = locationmap.LocationMap()

    def loadPath(self, path):
        basedir = os.path.dirname(path)
        f = open(path, "rU")
        p = cfgparser.Parser(f, path, SCHEMA)
        cf = p.load()
        for value in cf.repository_map:
            if not value:
                raise ValueError("'repository-map' requires a location")
            type, rest = urllib.splittype(value)
            if not type:
                # local path references are relative to the file
                # we're loading
                value = os.path.join(basedir, value)
            self.location_maps.append(value)


def defaultConfigurationPath():
    """Return the path name of the zpkg configuration file.

    This returns different things for Windows and POSIX systems.
    """
    zpkgdir = "zpkg"
    if os.name == "posix":
        zpkgdir = "." + zpkgdir
    name = os.path.join("~", zpkgdir, "zpkg.conf")
    path = os.path.expanduser(name)
    if os.path.exists(path):
        path = os.path.realpath(path)
    return path

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

from zpkgtools import locationmap


class Configuration:
    """Configuration settings for zpkg."""

    def __init__(self, path=None):
        self.location_maps = []
        self.locations = None
        if path is None:
            path = defaultConfigurationPath()
            if os.path.exists(path):
                self.loadPath(path)
        else:
            self.loadPath(path)

    def finalize(self):
        for loc in self.location_maps:
            self.locations = locationmap.fromPathOrUrl(loc,
                                                       mapping=self.locations)
        if self.locations is None:
            self.locations = locationmap.LocationMap()

    def loadPath(self, path):
        basedir = os.path.dirname(path)
        f = open(path, "rU")
        for line in f:
            line = line.strip()
            if line[:1] in ("", "#"):
                continue
            parts = line.split(None, 1)
            key = parts[0]
            if len(parts) == 2:
                # The replace is needed to ensure that we're close to
                # ZConfig syntax; we should check also for single
                # dollar signs and forbid them.
                value = parts[1].replace("$$", "$")
            else:
                value = None
            if key == "repository-map":
                if value is None:
                    raise ValueError("'repository-map' requires a location")
                type, rest = urllib.splittype(value)
                if not type:
                    # local path references are relative to the file
                    # we're loading
                    value = os.path.join(basedir, value)
                self.location_maps.append(value)
            else:
                raise ValueError("unknown configuration setting: %r" % key)


def defaultConfigurationPath():
    """Return the path name of the zpkg configuration file.

    This returns different things for Windows and POSIX systems.
    """
    if os.name == "posix":
        name = "~/.zpkgrc"
    else:
        name = os.path.join("~", "zpkg.conf")
    path = os.path.expanduser(name)
    if os.path.exists(path):
        path = os.path.realpath(path)
    return path

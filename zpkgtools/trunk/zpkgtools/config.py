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
"""Configuration support for **zpkg**.

:undocumented: non_empty_string resource_map
"""

import os
import urllib
import urlparse

from zpkgsetup import cfgparser
from zpkgsetup import urlutils
from zpkgtools import locationmap


get_schema = cfgparser.cachedSchemaLoader("config.xml")


def non_empty_string(string):
    if not string:
        raise ValueError("value cannot be empty")
    return string


def resource_map(value):
    return value.map


def exclude(value):
    return value.mapping.keys()


class Configuration:
    """Configuration settings for **zpkg**.

    :Ivariables:
      - `locations`: Mapping of resource identifiers to location URLs.

      - `location_maps`: List of location maps to load.

      - `include_support_code`: Indicates whether support code should
        be included in distributions.

      - `exclude_packages`: Resources to exclude from the package.
    """

    def __init__(self):
        """Initialize a new `Configuration` object."""
        self.application = False
        self.collect_dependencies = False
        self.location_maps = []
        self.locations = locationmap.LocationMap()
        self.exclude_packages = []
        self.include_support_code = True
        self.default_collection = None

    def finalize(self):
        """Load the location maps into `locations`."""
        for loc in self.location_maps:
            self.locations = locationmap.fromPathOrUrl(loc, self.locations)

    def loadPath(self, path):
        """Load configuration from a file.

        :param path: Path of the file to load.

        :raises IOError: If the `path` cannot be found, is not a file,
          or cannot be read.
        """
        basedir = os.path.dirname(path)
        f = open(path, "rU")
        try:
            self.loadStream(f, path, basedir)
        finally:
            f.close()

    def loadStream(self, f, path, basedir):
        """Load configuration from an open stream.

        :Parameters:
          - `f`: The stream, which must have been opened for reading
            in text mode.

          - `path`: Path with which to identify the stream in error
            messages.

          - `basedir`: Base directory with which to join relative
            paths found in the configuration file.

        """
        if basedir:
            basedir = os.path.abspath(basedir)
        else:
            basedir = os.getcwd()
        schema = get_schema()
        url = urlutils.file_url(os.path.abspath(path))
        cf, _ = cfgparser.loadConfigFile(schema, f, url)
        # deal with embedded resource maps:
        for map in cf.resource_maps:
            for key, value in map.iteritems():
                value = urlparse.urljoin(url, value)
                if key.endswith(".*"):
                    wildcard = key[:-2]
                    if not self.locations._have_wildcard(wildcard):
                        self.locations._add_wildcard(wildcard, value)
                elif key not in self.locations:
                    self.locations[key] = value
        self.application = cf.build_application
        self.collect_dependencies = cf.collect_dependencies
        self.default_collection = cf.default_collection
        self.include_support_code = cf.include_support_code
        self.resource_maps = cf.resource_maps
        self.exclude_packages = cf.exclude_packages
        for value in cf.location_maps:
            value = urlparse.urljoin(url, value)
            self.location_maps.append(value)


def defaultConfigurationPath():
    """Return the path name of the configuration file.

    This returns different things for Windows and POSIX systems.

    :return: Path to the default configuration file.  The directory or
      file may not exist.
    """
    zpkgdir = "zpkg"
    if os.name == "posix":
        zpkgdir = "." + zpkgdir
    name = os.path.join("~", zpkgdir, "zpkg.conf")
    return os.path.expanduser(name)

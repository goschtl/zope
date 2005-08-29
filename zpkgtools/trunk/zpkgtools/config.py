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

The syntax of the configuration files is incredibly simple, but is
intended to be a strict subset of the `ZConfig`_.  This allows us to
switch to `ZConfig`_ in the future if we decide the dependency is
worth it.

.. _ZConfig:  http://www.zope.org/Members/fdrake/zconfig/

:undocumented: boolean non_empty_string \*_STRINGS
"""

import os
import urllib
import urlparse

from zpkgsetup import cfgparser
from zpkgsetup import urlutils
from zpkgtools import locationmap


TRUE_STRINGS =("yes", "true", "on")
FALSE_STRINGS = ("no", "false", "off")

def boolean(string):
    s = string.lower()
    if s in FALSE_STRINGS:
        return False
    if s in TRUE_STRINGS:
        return True
    raise ValueError("unknown boolean value: %r" % string)

def non_empty_string(string):
    if not string:
        raise ValueError("value cannot be empty")
    return string


class Schema(cfgparser.Schema, object):

    def __init__(self, filename, locations):
        # We can use the base schema for the top-level definitions,
        # except for the <resources> section.
        super(Schema, self).__init__(
            ({"resource-map": non_empty_string,
              "include-support-code": boolean,
              "collect-dependencies": boolean,
              "build-application": boolean,
              "default-collection": non_empty_string,
              }, ["resources"], None))
        self.base = urlutils.file_url(filename)
        self.filename = filename
        self.locations = locations

    def startSection(self, parent, typename, name):
        if typename != "resources":
            raise cfgparser.ConfigurationError(
                "only <resources> sections are allowed")
        if isinstance(parent, locationmap.MapLoader):
            raise cfgparser.ConfigurationError(
                "<resources> sections may not be nested")
        return locationmap.MapLoader(self.base, self.filename, self.locations)

    def addValue(self, section, key, value):
        if isinstance(section, locationmap.MapLoader):
            section.add(key, value)
        else:
            super(Schema, self).addValue(section, key, value)

    def finishSection(self, section):
        if isinstance(section, locationmap.MapLoader):
            return section.mapping
        return super(Schema, self).finishSection(section)



class Configuration:
    """Configuration settings for **zpkg**.

    :Ivariables:
      - `locations`: Mapping of resource identifiers to location URLs.

      - `location_maps`: List of location maps to load.

      - `include_support_code`: Indicates whether support code should
        be included in distributions.
    """

    def __init__(self):
        """Initialize a new `Configuration` object."""
        self.application = False
        self.collect_dependencies = False
        self.location_maps = []
        self.locations = locationmap.LocationMap()
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
        p = cfgparser.Parser(f, path, Schema(os.path.abspath(path),
                                             self.locations))
        cf = p.load()
        base = urlutils.file_url(basedir) + "/"
        for value in cf.resource_map:
            value = urlparse.urljoin(base, value)
            self.location_maps.append(value)
        # include-support-code
        if len(cf.include_support_code) > 1:
            raise cfgparser.ConfigurationError(
                "include-support-code can be specified at most once")
        if cf.include_support_code:
            self.include_support_code = cf.include_support_code[0]
        # collect-dependencies
        if len(cf.collect_dependencies) > 1:
            raise cfgparser.ConfigurationError(
                "collect-dependencies can be specified at most once")
        if cf.collect_dependencies:
            self.collect_dependencies = cf.collect_dependencies[0]
        # build-application
        if len(cf.build_application) > 1:
            raise cfgparser.ConfigurationError(
                "build-application can be specified at most once")
        if cf.build_application:
            self.application = cf.build_application[0]
        # default-collection
        if len(cf.default_collection) > 1:
            raise cfgparser.ConfigurationError(
                "default-collection can be specified at most once")
        if cf.default_collection:
            self.default_collection = cf.default_collection[0]


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

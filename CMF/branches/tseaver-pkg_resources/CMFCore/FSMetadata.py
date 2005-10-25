##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Handles reading the properties for an object that comes from the filesystem.

$Id$
"""

from ConfigParser import ConfigParser
from pkg_resources import resource_stream
import re
import sys
from warnings import warn

from zLOG import LOG, ERROR

class CMFConfigParser(ConfigParser):
    """ This our wrapper around ConfigParser to
    solve a few minor niggles with the code """
    # adding in a space so that names can contain spaces
    OPTCRE = re.compile(
        r'(?P<option>[]\-[ \w_.*,(){}]+)'      # a lot of stuff found by IvL
        r'[ \t]*(?P<vi>[:=])[ \t]*'           # any number of space/tab,
                                              # followed by separator
                                              # (either : or =), followed
                                              # by any # space/tab
        r'(?P<value>.*)$'                     # everything up to eol
        )

    def optionxform(self, optionstr):
        """
        Stop converting the key to lower case, very annoying for security etc
        """
        return optionstr.strip()

class FSMetadata:
    # public API
    _package = None
    _entry_subpath = None
    _filename = None
    def __init__(self, package=None, entry_subpath=None, filename=None):
        MESSAGE = ("Either 'filename' or 'package' + 'entry_subpath' must "
                   "be supplied.")
        if filename is None:
            if package is None or entry_subpath is None:
                raise ValueError(MESSAGE)
            self._package = package
            self._entry_subpath = entry_subpath
        else:
            if package is not None or entry_subpath is not None:
                raise ValueError(MESSAGE)
            self._filename = filename

    def read(self):
        """ Find the file(s) and read them.
        
        o Prefer new '.metdata' file.
        
        o Fall back to '.properties' and '.security' files.
        """
        self._readMetadata()

    def getProxyRoles(self):
        """ Returns the proxy roles """
        if self.getProperties():
            pxy = self.getProperties().get('proxy')
            if pxy:
                return [r.strip() for r in pxy.split(',') if r.strip()]
        return []

    def getSecurity(self):
        """ Gets the security settings """
        return self._security

    def getProperties(self):
        """ Gets the properties settings """
        return self._properties

    # private API
    def _readMetadata(self):
        """ Read the new file format using ConfigParser """
        self._properties = {}
        self._security = {}

        try:
            stream = self._getStream()
            if stream is None:
                return

            cfg = CMFConfigParser()
            cfg.readfp(stream)

            # the two sections we care about
            self._properties = self._getSectionDict(cfg, 'Default')
            self._security = self._getSectionDict(cfg, 'Security',
                                                  self._securityParser)
        except:
            LOG('FSMetadata',
                 ERROR,
                'Error parsing .metadata file',
                 error=sys.exc_info())

        # to add in a new value such as proxy roles,
        # just add in the section, call it using getSectionDict
        # if you need a special parser for some whacky
        # config, then just pass through a special parser


    def _getStream(self):
        """ Return a stream opened against our .metadata file
        
        o File may be found either via 'pkg_resoruces' or via direct
          file access.
        """
        if self._package is not None:
            try:
                filename = '%s%s' % (self._entry_subpath, '.metadata')
                return resource_stream(self._package, filename)
            except IOError:
                return None
        try:
            return open(self._filename + '.metadata', 'r')
        except IOError:
            return None
            
    def _nullParser(self, data):
        """
        This is the standard rather boring null parser that does very little
        """
        return data

    def _securityParser(self, data):
        """ A specific parser for security lines

        Security lines must be of the format

        Permission = (0|1):Role[,Role...]

        Where 0|1 is the acquire permission setting
        and Role is the roles for this permission
        eg: 1:Manager or 0:Manager,Anonymous
        """
        if data.find(':') < 1:
            raise ValueError, "The security declaration of file " + \
                  "%r is in the wrong format" % self._filename

        acquire, roles = data.split(':')
        roles = [r.strip() for r in roles.split(',') if r.strip()]
        return (int(acquire), roles)

    def _getSectionDict(self, cfg, section, parser=None):
        """
        Get a section and put it into a dict, mostly a convenience
        function around the ConfigParser

        Note: the parser is a function to parse each value, so you can
        have custom values for the key value pairs
        """
        if parser is None:
            parser = self._nullParser

        props = {}
        if cfg.has_section(section):
            for opt in cfg.options(section):
                props[opt] = parser(cfg.get(section, opt))
            return props

        # we need to return None if we have none to be compatible
        # with existing API
        return None

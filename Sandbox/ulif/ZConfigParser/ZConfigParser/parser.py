##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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
"""Configuration parser."""

from ConfigParser import ConfigParser
from ZConfigParser.convert import convertFile

class ZConfigParser(ConfigParser):

    def read(self, filenames):
        """Read a list of configuration files.

        If a filename has a ``.conf`` extension, it is converted into
        .ini-style on-the-fly before being parsed.
        """
        real_filenames = []
        if isinstance(filenames, basestring):
            filenames = [filenames]
        for filename in filenames:
            if filename.endswith('.conf'):
                new_filename = filename[:-5] + '.ini'
                converted_file = convertFile(filename)
                # XXX: We should write generated files to a safe location.
                open(new_filename, 'wb').write(converted_file)
                filename = new_filename
                pass
            real_filenames.append(filename)
        result = ConfigParser.read(self, real_filenames)
        # XXX: remove temporary files
        return result

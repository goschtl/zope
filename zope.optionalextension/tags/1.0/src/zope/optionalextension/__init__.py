##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
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
from distutils.command.build_ext import build_ext
from distutils.errors import CCompilerError
from distutils.errors import DistutilsExecError
from distutils.errors import DistutilsPlatformError
import sys
from traceback import format_exc
 
 
class optional_build_ext(build_ext):
    """ Allow building of C extensions to fail without blocking installation.
    """
    description = __doc__

    def __init__ (self, dist, stream=None):
        build_ext.__init__(self, dist)
        if stream is None:
            stream = sys.stderr
        self._stream = stream

    def run(self):
        try:
            build_ext.run(self)
        except DistutilsPlatformError, e:
            self._unavailable(e)

    def build_extension(self, ext):
        try:
            build_ext.build_extension(self, ext)
        except (CCompilerError, DistutilsExecError), e:
            self._unavailable(e)

    def _unavailable(self, e):
        self._stream.write('%s\n' % ('*' * 80))
        self._stream.write("""WARNING:

        An optional code optimization (C extension) could not be compiled.
        """)
        self._stream.write('\n')
        self._stream.write('%s\n' % format_exc(e))
        self._stream.write('%s\n' % ('*' * 80))

##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""

$Id: FileResource.py,v 1.2 2002/12/02 10:03:18 ryzaja Exp $
"""
__metaclass__ = type # All classes are new style when run with Python 2.2+


from Zope.Misc.content_types import guess_content_type
from Zope.Misc.package_home import package_home
from Zope.Misc.standard_dates import rfc1123_date
from Zope.Exceptions import NotFoundError
from time import time
from os import stat
import os

class File:
    """Image objects stored in external files."""

    def __init__(self, path):

        self.path=path

        file=open(path, 'rb')
        data=file.read()
        file.close()
        self.content_type, enc = guess_content_type(path, data)
        self.__name__=path[path.rfind('/')+1:]
        self.lmt=float(stat(path)[8]) or time()
        self.lmh=rfc1123_date(self.lmt)

class Image(File):

    def __init__(self, path):
        super(Image, self).__init__(path)
        if self.content_type in (None,  'application/octet-stream'):
            ext = os.path.splitext(self.path)[1]
            if ext:
                self.content_type='image/%s' % ext[1:]
    

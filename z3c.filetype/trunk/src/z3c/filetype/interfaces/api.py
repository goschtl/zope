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
""" api interfaces

$Id$
"""
from zope import interface


class IAPI(interface.Interface):
    """ filetype api """

    def byMimeType(mt):
        """returns interfaces implemented by mimeType"""

    def getInterfacesFor(file, filename=None, mimeType=None):
        """ returns a sequence of interfaces that are provided by file like
        objects (file argument) with an optional
        filename as name or mimeType as mime-type """

    def getInterfacesForFile(filename, mimeType=None):
        """ returns a sequence of interfaces that are provided by file 
        with filename as name and optional mimeType as mime-type """

    def getInterfacesForFilename(filename):
        """ returns a sequence of interfaces that are provided by filename """

    def applyInterfaces(obj):
        """ detect object mimetypes and set mimetype interfaces """

    def convert(obj, mimetype):
        """ convert obj to destination mimetype """

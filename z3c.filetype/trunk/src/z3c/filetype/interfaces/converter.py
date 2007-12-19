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
""" converter interfaces

$Id$
"""
from zope import interface


class ConverterException(Exception):
    """ base converter exception """


class ConverterNotFound(Exception):
    """ required converter not found """


class IConverterModule(interface.Interface):
    """ converter module """

    def convert(context, mimetype):
        """ convert `context` data to mimetype data, return ITypeableFile object """


class IConverter(interface.Interface):
    """ base interface for data converter """

    def __init__(context, destination):
        """ adapter """

    def convert():
        """ convert data """


class ISimpleImageConverter(IConverter):
    """ simple image converter """

    def convert(width=None, height=None, scale=0):
        """ convert image """

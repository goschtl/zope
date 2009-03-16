##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
""" 

$Id:  2007-12-12 12:27:02Z fafhrd $
"""
from zope import interface, schema


class ICategory(interface.Interface):
    
    category = schema.TextLine(
        title = u'Category',
        required = False)


class IPrefs1(interface.Interface):

    name = schema.TextLine(
        title = u'Name',
        required = True)


class IPrefs2(interface.Interface):

    location = schema.TextLine(
        title = u'Location',
        default = u'',
        required = False)


class IPrefs3(interface.Interface):

    location = schema.TextLine(
        title = u'Location',
        default = u'',
        required = False)


class IPrefs4(interface.Interface):

    prefs4 = schema.TextLine(
        title = u'Prefs4',
        default = u'',
        required = False)

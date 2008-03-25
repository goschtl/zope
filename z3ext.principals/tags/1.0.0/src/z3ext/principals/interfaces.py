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
""" z3ext.principals interfaces

$Id$
"""
from zope import interface
from zope.viewlet.interfaces import IViewletManager


class IPrincipalType(interface.Interface):
    """ principal content type """


class IPrincipalsManagement(interface.Interface):
    """ princiapals management """


class IPrincipalPreferences(interface.Interface):
    """ marker interface for preferences """


class IPrincipalFactory(interface.Interface):
    """ principal factory """

    name = interface.Attribute('Name')

    title = interface.Attribute('Title')

    description = interface.Attribute('Description')

    def __init__(context, request):
        """ adapter factory """


class IPrincipalInformation(IViewletManager):
    """ extra preferences viewlet manager """

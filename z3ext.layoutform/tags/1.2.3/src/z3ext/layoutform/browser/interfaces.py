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
from zope import interface


class IForm(interface.Interface):
    """ form view """


class IExtraFormInfo(interface.Interface):
    """ extra form information """


class IViewspace(interface.Interface):
    """ form viewspace """


class IExtraViewspaceInfo(interface.Interface):
    """ extra widget information """


class IWidget(interface.Interface):
    """ widget view """


class IExtraBeforeWidget(interface.Interface):
    """ extra widget information """


class IExtraAfterWidget(interface.Interface):
    """ extra widget information """


class IGroup(interface.Interface):
    """ group """


class IFormGroups(interface.Interface):
    """ form groups """


class IFormButtons(interface.Interface):
    """ form buttons """


class IExtraFormButtonsInfo(interface.Interface):
    """ extra buttons information """

##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
"""this module implements the flickr.contacts namespace

http://www.flickr.com/services/api/

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema
from zope.schema import fieldproperty
from lovely.flickr import interfaces, flickr


class Contacts(list):
    zope.interface.implements(interfaces.IContacts)

    @classmethod
    def fromElement(self, element):
        """See interfaces.IBaseFlickrObject"""
        contacts = Contacts()
        for child in element.getchildren():
            contacts.append(Contact.fromElement(child))
        return contacts

    def __repr__(self):
        return '<%s entries=%i>' %(self.__class__.__name__, len(self))

class Contact(object):
    zope.interface.implements(interfaces.IContact)

    nsid = fieldproperty.FieldProperty(interfaces.IContact['nsid'])
    username = fieldproperty.FieldProperty(interfaces.IContact['username'])
    iconserver = fieldproperty.FieldProperty(interfaces.IContact['iconserver'])
    realname = fieldproperty.FieldProperty(interfaces.IContact['realname'])
    friend = fieldproperty.FieldProperty(interfaces.IContact['friend'])
    family = fieldproperty.FieldProperty(interfaces.IContact['family'])
    ignored = fieldproperty.FieldProperty(interfaces.IContact['ignored'])

    def __init__(self, nsid, username, iconserver, ignored, realname=None,
                 friend=None, family=None):
        self.nsid = nsid
        self.username = username
        self.iconserver = iconserver
        self.realname = realname
        self.friend = friend
        self.family = family
        self.ignored = ignored

    @classmethod
    def fromElement(self, element):
        """See interfaces.IBaseFlickrObject"""
        args = dict([
            (name, field.fromUnicode(unicode(element.get(name))))
            for name, field in zope.schema.getFields(interfaces.IContact).items()
            if element.get(name) is not None
            ])
        return Contact(**args)

    def __repr__(self):
        return '<%s %s>' %(self.__class__.__name__, self.nsid)


class APIContacts(flickr.APIFlickr):
    zope.interface.implements(interfaces.IAPIContacts)

    def getList(self, filter=None):
        """See interfaces.IAPIContacts"""
        params = self.initParameters('flickr.contacts.getList')
        if filter is not None:
            assert filter in ['friends', 'family', 'both', 'neither']
            params['filter'] = filter
        self.addAuthToken(params)
        self.sign(params)
        elem = self.execute(params)
        return Contacts.fromElement(elem.getchildren()[0])

    def getPublicList(self, user_name):
        """See interfaces.IAPIContacts"""
        params = self.initParameters('flickr.contacts.getPublicList',
                                     user_name=user_name)
        elem = self.execute(params)
        return Contacts.fromElement(elem.getchildren()[0])


def getList(api_key, auth_token, **kw):
    __doc__ = interfaces.IAPIContacts['getList'].__doc__

    return APIContacts(api_key, secret, auth_token).getList(**kw)

def getPublicList(api_key, **kw):
    __doc__ = interfaces.IAPIContacts['getPublicList'].__doc__

    return APIContacts(api_key).getPublicList(**kw)

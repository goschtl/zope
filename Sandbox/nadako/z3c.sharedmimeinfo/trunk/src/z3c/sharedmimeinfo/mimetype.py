##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""MIME type helper objects

$Id$
"""
import os
from xml.dom import minidom, XML_NAMESPACE

from zope.interface import implements
from zope.i18n.simpletranslationdomain import SimpleTranslationDomain
from zope.i18nmessageid import MessageFactory

from z3c.sharedmimeinfo.interfaces import IMIMEType
from z3c.sharedmimeinfo.util import iterDataPaths

SMI_NAMESPACE = 'http://www.freedesktop.org/standards/shared-mime-info'

msgfactory = MessageFactory('shared-mime-info')
mimeTypesTranslationDomain = SimpleTranslationDomain('shared-mime-info')

_mime_type_cache = {}

class MIMEType(unicode):
    """Single MIME type representation"""

    implements(IMIMEType)
    
    __slots__ = ('_media', '_subtype', '_title')

    def __new__(cls, media, subtype=None):
        if subtype is None and '/' in media:
            media, subtype = media.split('/', 1)

        if (media, subtype) in _mime_type_cache:
            return _mime_type_cache[(media, subtype)]
        obj = super(MIMEType, cls).__new__(cls, media+'/'+subtype)
        obj._media = unicode(media)
        obj._subtype = unicode(subtype)
        obj._title = None
        for path in iterDataPaths(os.path.join('mime', media, subtype + '.xml')):
            doc = minidom.parse(path)
            if doc is None:
                continue
            for comment in doc.documentElement.getElementsByTagNameNS(SMI_NAMESPACE, 'comment'):
                data = ''.join([n.nodeValue for n in comment.childNodes]).strip()
                lang = comment.getAttributeNS(XML_NAMESPACE, 'lang')
                msgid = '%s/%s' % (media, subtype)
                if not lang:
                    obj._title = msgfactory(msgid, default=data)
                else:
                    mimeTypesTranslationDomain.messages[(lang, msgid)] = data
        _mime_type_cache[(media, subtype)] = obj
        return obj

    title = property(lambda self:self._title or unicode(self))
    media = property(lambda self:self._media)
    subtype = property(lambda self:self._subtype)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, str(self))

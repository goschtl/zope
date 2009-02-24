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
'''MIME type helper objects

$Id$
'''
import os
from xml.dom import minidom, XML_NAMESPACE

from zope.interface import implements
from zope.i18n.simpletranslationdomain import SimpleTranslationDomain
from zope.i18nmessageid import MessageFactory

from z3c.mimetype.interfaces import IMIMEType
from z3c.mimetype.util import iterDataPaths

SMI_NAMESPACE = 'http://www.freedesktop.org/standards/shared-mime-info'
MIME_TYPES = {}

msgfactory = MessageFactory('shared-mime-info')

mimeTypesTranslationDomain = SimpleTranslationDomain('shared-mime-info')

def lookup(media, subtype=None):
    '''Lookup a MIMEType object using either two arguments (media and subtype)
    or one argument in ``media/subtype`` form.
    '''
    
    if subtype is None and '/' in media:
        media, subtype = media.split('/', 1)
    if (media, subtype) not in MIME_TYPES:
        MIME_TYPES[(media, subtype)] = _MIMEType(media, subtype)
    return MIME_TYPES[(media, subtype)]

class _MIMEType(object):
    '''Single MIME type representation
    
    Never create these objects using this class, use the ``lookup`` function
    defined above instead.
    '''

    implements(IMIMEType)

    _title = None

    def __init__(self, media, subtype):
        assert media and '/' not in media
        assert subtype and '/' not in subtype
        assert (media, subtype) not in MIME_TYPES
        self.media = media
        self.subtype = subtype
        for path in iterDataPaths(os.path.join('mime', media, subtype + '.xml')):
            doc = minidom.parse(path)
            if doc is None:
                continue
            for comment in doc.documentElement.getElementsByTagNameNS(SMI_NAMESPACE, 'comment'):
                data = ''.join([n.nodeValue for n in comment.childNodes]).strip()
                lang = comment.getAttributeNS(XML_NAMESPACE, 'lang')
                msgid = '%s/%s' % (media, subtype)
                if not lang:
                    self._title = msgfactory(msgid, default=data)
                else:
                    mimeTypesTranslationDomain.messages[(lang, msgid)] = data

    @property
    def title(self):
        return self._title or unicode(self)

    def __str__(self):
        return self.media + '/' + self.subtype

    def __repr__(self):
        return '<%s %s/%s>' % (self.__class__.__name__, self.media, self.subtype)

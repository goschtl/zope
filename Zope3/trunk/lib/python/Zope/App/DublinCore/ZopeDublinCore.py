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
$Id: ZopeDublinCore.py,v 1.2 2002/10/04 19:05:50 jim Exp $
"""

__metaclass__ = type

from Zope.App.DublinCore.IZopeDublinCore import IZopeDublinCore
from Zope.Misc.DateTimeParse import parseDatetimetz
from datetime import datetimetz
from datetime import datetime

class SimpleProperty:

    def __init__(self, name):
        self.__name__ = name

class ScalarProperty(SimpleProperty):
        
    def __get__(self, inst, klass):
        if inst is None:
            return self
        data = inst._mapping.get(self.__name__, ())
        if data:
            return data[0]
        else:
            return u''

    def __set__(self, inst, value):
        if not isinstance(value, unicode):
            raise TypeError("Element must be unicode")

        dict = inst._mapping
        __name__ = self.__name__
        inst._changed()
        dict[__name__] = (value, ) + dict.get(__name__, ())[1:]

def _scalar_get(inst, name):
    data = inst._mapping.get(name, ())
    if data:
        return data[0]
    else:
        return u''
    
class DateProperty(ScalarProperty):
        
    def __get__(self, inst, klass):
        if inst is None:
            return self
        data = inst._mapping.get(self.__name__, ())
        if data:
            return parseDatetimetz(data[0])
        else:
            return None

    def __set__(self, inst, value):
        if not isinstance(value, datetime):
            raise TypeError("Element must be %s", datetimetz)

        value = unicode(value.isoformat('T'), 'ascii')

        super(DateProperty, self).__set__(inst, value)

        
class SequenceProperty(SimpleProperty):
        
    def __get__(self, inst, klass):
        if inst is None:
            return self

        return inst._mapping.get(self.__name__, ())

    def __set__(self, inst, value):
        value = tuple(value)
        for v in value:
            if not isinstance(v, unicode):
                raise TypeError("Elements must be unicode")
        inst._changed()
        inst._mapping[self.__name__] = value
    
class ZopeDublinCore:
    """Zope Dublin Core Mixin

    Subclasses should define either _changed() or _p_changed.

    Just mix with Persistence to get a persistent version.
    """


    __implements__ =  IZopeDublinCore

    def __init__(self, mapping=None):
        if mapping is None:
            mapping = {}
        self._mapping = mapping

    def _changed(self):
        self._p_changed = 1

    title = ScalarProperty(u'Title')
    
    def Title(self):
        "See Zope.App.DublinCore.IZopeDublinCore.IZopeDublinCore"
        return self.title

    creators = SequenceProperty(u'Creator')
    
    def Creator(self):
        "See Zope.App.DublinCore.IZopeDublinCore.IZopeDublinCore"
        return self.creators

    subjects = SequenceProperty(u'Subject')

    def Subject(self):
        "See Zope.App.DublinCore.IZopeDublinCore.IZopeDublinCore"
        return self.subjects

    description = ScalarProperty(u'Description')

    def Description(self):
        "See Zope.App.DublinCore.IZopeDublinCore.IZopeDublinCore"
        return self.description

    publisher = ScalarProperty(u'Publisher')

    def Publisher(self):
        "See Zope.App.DublinCore.IZopeDublinCore.IZopeDublinCore"
        return self.publisher

    contributors = SequenceProperty(u'Contributor')

    def Contributors(self):
        "See Zope.App.DublinCore.IZopeDublinCore.IZopeDublinCore"
        return self.contributors

    def Date(self):
        "See Zope.App.DublinCore.IZopeDublinCore.IZopeDublinCore"
        return _scalar_get(self, u'Date')

    created = DateProperty(u'Date.Created')

    def CreationDate(self):
        "See Zope.App.DublinCore.IZopeDublinCore.IZopeDublinCore"
        return _scalar_get(self, u'Date.Created')

    effective = DateProperty(u'Date.Effective')

    def EffectiveDate(self):
        "See Zope.App.DublinCore.IZopeDublinCore.IZopeDublinCore"
        return _scalar_get(self, u'Date.Effective')

    expires = DateProperty(u'Date.Expires')

    def ExpirationDate(self):
        "See Zope.App.DublinCore.IZopeDublinCore.IZopeDublinCore"
        return _scalar_get(self, u'Date.Expires')

    modified = DateProperty(u'Date.Modified')

    def ModificationDate(self):
        "See Zope.App.DublinCore.IZopeDublinCore.IZopeDublinCore"
        return _scalar_get(self, u'Date.Modified')

    type = ScalarProperty(u'Type')

    def Type(self):
        "See Zope.App.DublinCore.IZopeDublinCore.IZopeDublinCore"
        # XXX what is this?
        return self.type

    format = ScalarProperty(u'Format')

    def Format(self):
        "See Zope.App.DublinCore.IZopeDublinCore.IZopeDublinCore"
        # XXX what is this?
        return self.format

    identifier = ScalarProperty(u'Identifier')

    def Identifier(self):
        "See Zope.App.DublinCore.IZopeDublinCore.IZopeDublinCore"
        # XXX what is this?
        return self.identifier

    language = ScalarProperty(u'Language')

    def Language(self):
        "See Zope.App.DublinCore.IZopeDublinCore.IZopeDublinCore"
        return self.language

    rights = ScalarProperty(u'Rights')

    def Rights(self):
        "See Zope.App.DublinCore.IZopeDublinCore.IZopeDublinCore"
        return self.rights

    def setQualifiedTitles(self, qualified_titles):
        "See Zope.App.DublinCore.IWritableDublinCore.IWritableDublinCore"
        return _set_qualified(self, u'Title', qualified_titles)

    def setQualifiedCreators(self, qualified_creators):
        "See Zope.App.DublinCore.IWritableDublinCore.IWritableDublinCore"
        return _set_qualified(self, u'Creator', qualified_creators)

    def setQualifiedSubjects(self, qualified_subjects):
        "See Zope.App.DublinCore.IWritableDublinCore.IWritableDublinCore"
        return _set_qualified(self, u'Subject', qualified_subjects)

    def setQualifiedDescriptions(self, qualified_descriptions):
        "See Zope.App.DublinCore.IWritableDublinCore.IWritableDublinCore"
        return _set_qualified(self, u'Description', qualified_descriptions)

    def setQualifiedPublishers(self, qualified_publishers):
        "See Zope.App.DublinCore.IWritableDublinCore.IWritableDublinCore"
        return _set_qualified(self, u'Publisher', qualified_publishers)

    def setQualifiedContributors(self, qualified_contributors):
        "See Zope.App.DublinCore.IWritableDublinCore.IWritableDublinCore"
        return _set_qualified(self, u'Contributor', qualified_contributors)

    def setQualifiedDates(self, qualified_dates):
        "See Zope.App.DublinCore.IWritableDublinCore.IWritableDublinCore"
        return _set_qualified(self, u'Date', qualified_dates)

    def setQualifiedTypes(self, qualified_types):
        "See Zope.App.DublinCore.IWritableDublinCore.IWritableDublinCore"
        return _set_qualified(self, u'Type', qualified_types)

    def setQualifiedFormats(self, qualified_formats):
        "See Zope.App.DublinCore.IWritableDublinCore.IWritableDublinCore"
        return _set_qualified(self, u'Format', qualified_formats)

    def setQualifiedIdentifiers(self, qualified_identifiers):
        "See Zope.App.DublinCore.IWritableDublinCore.IWritableDublinCore"
        return _set_qualified(self, u'Identifier', qualified_identifiers)

    def setQualifiedSources(self, qualified_sources):
        "See Zope.App.DublinCore.IWritableDublinCore.IWritableDublinCore"
        return _set_qualified(self, u'Source', qualified_sources)

    def setQualifiedLanguages(self, qualified_languages):
        "See Zope.App.DublinCore.IWritableDublinCore.IWritableDublinCore"
        return _set_qualified(self, u'Language', qualified_languages)

    def setQualifiedRelations(self, qualified_relations):
        "See Zope.App.DublinCore.IWritableDublinCore.IWritableDublinCore"
        return _set_qualified(self, u'Relation', qualified_relations)

    def setQualifiedCoverages(self, qualified_coverages):
        "See Zope.App.DublinCore.IWritableDublinCore.IWritableDublinCore"
        return _set_qualified(self, u'Coverage', qualified_coverages)

    def setQualifiedRights(self, qualified_rights):
        "See Zope.App.DublinCore.IWritableDublinCore.IWritableDublinCore"
        return _set_qualified(self, u'Rights', qualified_rights)

    def getQualifiedTitles(self):
        "See Zope.App.DublinCore.IStandardDublinCore.IStandardDublinCore"
        return _get_qualified(self, u'Title')

    def getQualifiedCreators(self):
        "See Zope.App.DublinCore.IStandardDublinCore.IStandardDublinCore"
        return _get_qualified(self, u'Creator')

    def getQualifiedSubjects(self):
        "See Zope.App.DublinCore.IStandardDublinCore.IStandardDublinCore"
        return _get_qualified(self, u'Subject')

    def getQualifiedDescriptions(self):
        "See Zope.App.DublinCore.IStandardDublinCore.IStandardDublinCore"
        return _get_qualified(self, u'Description')

    def getQualifiedPublishers(self):
        "See Zope.App.DublinCore.IStandardDublinCore.IStandardDublinCore"
        return _get_qualified(self, u'Publisher')

    def getQualifiedContributors(self):
        "See Zope.App.DublinCore.IStandardDublinCore.IStandardDublinCore"
        return _get_qualified(self, u'Contributor')

    def getQualifiedDates(self):
        "See Zope.App.DublinCore.IStandardDublinCore.IStandardDublinCore"
        return _get_qualified(self, u'Date')

    def getQualifiedTypes(self):
        "See Zope.App.DublinCore.IStandardDublinCore.IStandardDublinCore"
        return _get_qualified(self, u'Type')

    def getQualifiedFormats(self):
        "See Zope.App.DublinCore.IStandardDublinCore.IStandardDublinCore"
        return _get_qualified(self, u'Format')

    def getQualifiedIdentifiers(self):
        "See Zope.App.DublinCore.IStandardDublinCore.IStandardDublinCore"
        return _get_qualified(self, u'Identifier')

    def getQualifiedSources(self):
        "See Zope.App.DublinCore.IStandardDublinCore.IStandardDublinCore"
        return _get_qualified(self, u'Source')

    def getQualifiedLanguages(self):
        "See Zope.App.DublinCore.IStandardDublinCore.IStandardDublinCore"
        return _get_qualified(self, u'Language')

    def getQualifiedRelations(self):
        "See Zope.App.DublinCore.IStandardDublinCore.IStandardDublinCore"
        return _get_qualified(self, u'Relation')

    def getQualifiedCoverages(self):
        "See Zope.App.DublinCore.IStandardDublinCore.IStandardDublinCore"
        return _get_qualified(self, u'Coverage')

    def getQualifiedRights(self):
        "See Zope.App.DublinCore.IStandardDublinCore.IStandardDublinCore"
        return _get_qualified(self, u'Rights')


def _set_qualified(self, name, qvalue):
    data = {}
    dict = self._mapping
    
    for qualification, value in qvalue:
        data[qualification] = data.get(qualification, ()) + (value, )

    self._changed()
    for qualification, values in data.iteritems():
        qname = qualification and (name + '.' + qualification) or name
        dict[qname] = values

def _get_qualified(self, name):
    result = []
    for aname, avalue in self._mapping.iteritems():

        if aname == name:
            qualification = u''
            for value in avalue:
                result.append((qualification, value))
            
        elif aname.startswith(name):
            qualification = aname[len(name)+1:]
            for value in avalue:
                result.append((qualification, value))

    return tuple(result)
                              

__doc__ = ZopeDublinCore.__doc__ + __doc__


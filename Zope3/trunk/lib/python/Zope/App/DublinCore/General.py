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
"""Interfaces for getting standard dublin core data in it's full generality

$Id: General.py,v 1.2 2002/10/04 19:05:50 jim Exp $
"""

from Interface import Interface
from Zope.Schema import Text

class IDublinCoreElementItem(Interface):
    """A qualified sublin core element"""

    qualification = Text(title = u"Qualification",
                         description = u"The element qualification"
                         )

    value = Text(title = u"Value",
                 description = u"The element value",
                 )
    

class IGeneralDublinCore(Interface):
    """Dublin-core data access interface

    The Dublin Core, http://dublincore.org/, is a meta data standard
    that specifies a set of standard data elements. It provides
    flexibility of interpretation of these elements by providing for
    element qualifiers that specialize the meaning of specific
    elements. For example, a date element might have a qualifier, like
    "creation" to indicate that the date is a creation date. In
    addition, any element may be repeated. For some elements, like
    subject, and contributor, this is obviously necessary, but for
    other elements, like title and description, allowing repetitions
    is not very useful and adds complexity.

    This interface provides methods for retrieving data in full
    generality, to be complient with the dublin core standard.
    Other interfaces will provide more convenient access methods
    tailored to specific element usage patterns.
    """

    def getQualifiedTitles():
        """Return a sequence of Title IDublinCoreElementItem. 
        """

    def getQualifiedCreators():
        """Return a sequence of Creator IDublinCoreElementItem. 
        """

    def getQualifiedSubjects():
        """Return a sequence of Subject IDublinCoreElementItem. 
        """

    def getQualifiedDescriptions():
        """Return a sequence of Description IDublinCoreElementItem. 
        """

    def getQualifiedPublishers():
        """Return a sequence of Publisher IDublinCoreElementItem. 
        """

    def getQualifiedContributors():
        """Return a sequence of Contributor IDublinCoreElementItem. 
        """

    def getQualifiedDates():
        """Return a sequence of Date IDublinCoreElementItem. 
        """

    def getQualifiedTypes():
        """Return a sequence of Type IDublinCoreElementItem. 
        """

    def getQualifiedFormats():
        """Return a sequence of Format IDublinCoreElementItem. 
        """

    def getQualifiedIdentifiers():
        """Return a sequence of Identifier IDublinCoreElementItem. 
        """

    def getQualifiedSources():
        """Return a sequence of Source IDublinCoreElementItem. 
        """

    def getQualifiedLanguages():
        """Return a sequence of Language IDublinCoreElementItem. 
        """

    def getQualifiedRelations():
        """Return a sequence of Relation IDublinCoreElementItem. 
        """

    def getQualifiedCoverages():
        """Return a sequence of Coverage IDublinCoreElementItem. 
        """

    def getQualifiedRights():
        """Return a sequence of Rights IDublinCoreElementItem. 
        """

class IWritableGeneralDublinCore(Interface):
    """Provide write access to dublin core data

    This interface augments IStandardDublinCore with methods for
    writing elements.
    """
    
    def setQualifiedTitles(qualified_titles):
        """Set the qualified Title elements.

        The argument must be a sequence of IDublinCoreElementItem.
        """

    def setQualifiedCreators(qualified_creators):
        """Set the qualified Creator elements.
        
        The argument must be a sequence of Creator IDublinCoreElementItem. 
        """

    def setQualifiedSubjects(qualified_subjects): 
        """Set the qualified Subjects elements.

        The argument must be a sequence of Subject IDublinCoreElementItem. 
        """

    def setQualifiedDescriptions(qualified_descriptions):
        """Set the qualified Descriptions elements.

        The argument must be a sequence of Description IDublinCoreElementItem. 
        """

    def setQualifiedPublishers(qualified_publishers):
        """Set the qualified Publishers elements.

        The argument must be a sequence of Publisher IDublinCoreElementItem. 
        """

    def setQualifiedContributors(qualified_contributors):
        """Set the qualified Contributors elements.

        The argument must be a sequence of Contributor IDublinCoreElementItem. 
        """

    def setQualifiedDates(qualified_dates):
        """Set the qualified Dates elements.

        The argument must be a sequence of Date IDublinCoreElementItem. 
        """

    def setQualifiedTypes(qualified_types):
        """Set the qualified Types elements.

        The argument must be a sequence of Type IDublinCoreElementItem. 
        """

    def setQualifiedFormats(qualified_formats):
        """Set the qualified Formats elements.

        The argument must be a sequence of Format IDublinCoreElementItem. 
        """

    def setQualifiedIdentifiers(qualified_identifiers):
        """Set the qualified Identifiers elements.

        The argument must be a sequence of Identifier IDublinCoreElementItem. 
        """

    def setQualifiedSources(qualified_sources):
        """Set the qualified Sources elements.

        The argument must be a sequence of Source IDublinCoreElementItem. 
        """

    def setQualifiedLanguages(qualified_languages):
        """Set the qualified Languages elements.

        The argument must be a sequence of Language IDublinCoreElementItem. 
        """

    def setQualifiedRelations(qualified_relations):
        """Set the qualified Relations elements.

        The argument must be a sequence of Relation IDublinCoreElementItem. 
        """

    def setQualifiedCoverages(qualified_coverages):
        """Set the qualified Coverages elements.

        The argument must be a sequence of Coverage IDublinCoreElementItem. 
        """

    def setQualifiedRights(qualified_rights):
        """Set the qualified Rights elements.

        The argument must be a sequence of Rights IDublinCoreElementItem. 
        """

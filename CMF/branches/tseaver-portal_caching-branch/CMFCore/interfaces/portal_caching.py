##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
"""
    Declare interfaces for tool which maps skin methods to caching policies.
"""

from Interface import Attribute, Base

class CachePolicyPredicate(Base):
    """
        Rule matching a given content object / skin method to a 
        caching policy.
    """

    PREDICATE_TYPE = Attribute()

    def __call__( content, skin_method_name ):
        """
            Return true if the content object / skin method matches
            the rule.
        """

    def getTypeLabel():
        """
            Return a human-readable label for the kind of predicate.
        """

    def edit( **kw ):
        """
            Update the predicate.
        """

    def predicateWidget():
        """
            Return a snippet of HTML suitable for editing the
            predicate;  the snippet should arrange for values
            to be marshalled by ZPublisher as a ':record', with
            the ID of the predicate as the name of the record.

            The registry will call the predictate's 'edit' method,
            passing the fields of the record.
        """

class portal_caching( Base ):
    """
        Registry for rules which map content skins to cache managers.
    """

    def findCacheManager( content, skin_name ):
        """
            Perform a lookup over a collection of rules, returning the
            the cache manager object corresponding to content / skin_name,
            or None if no match found.
        """

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
""" Define tool implementing 'portal_caching' interface, plus appropriate
    predicates and rules.

$Id$
"""
__version__='$Revision$'[11:-2]

from OFS.SimpleItem import SimpleItem, Item
from AccessControl import ClassSecurityInfo
from Globals import DTMLFile, InitializeClass, PersistentMapping
from ZPublisher.mapply import mapply

from CMFCorePermissions import ManagePortal
from interfaces.portal_caching import CachePolicyPredicate, portal_caching

from utils import _dtmldir

import re, os, string, urllib

#
#   Predicate type registry
#
_predicate_types = []

def registerPredicateType( typeID, klass ):
    """
        Add a new predicate type.
    """
    _predicate_types.append( ( typeID, klass ) )

class DefaultPredicate( SimpleItem ):
    """
        Match anything (put this one last in the list).
    """
    __implements__ = CachePolicyPredicate
    PREDICATE_TYPE  = 'default'

    security = ClassSecurityInfo()
    security.declareObjectProtected( ManagePortal )

    def __init__( self, id ):
        self.id = id

    def __call__( self, content, skin_method_name ):
        " "
        return 1

    security.declareProtected( ManagePortal, 'getTypeLabel' )
    def getTypeLabel( self ):
        " "
        return self.PREDICATE_TYPE

    security.declareProtected( ManagePortal, 'edit' )
    def edit( self, **kw ):
        " "
        pass

    security.declareProtected( ManagePortal, 'predicateWidget' )
    predicateWidget = DTMLFile( 'cpp_defaultWidget', _dtmldir )

InitializeClass( DefaultPredicate )
registerPredicateType( DefaultPredicate.PREDICATE_TYPE, DefaultPredicate )

class NameSuffixPredicate( SimpleItem ):
    """
        Treat skin name suffix as "view type".
    """
    __implements__ = CachePolicyPredicate
    PREDICATE_TYPE  = 'name_suffix'

    _skin_name_suffix = None

    security = ClassSecurityInfo()
    security.declareObjectProtected( ManagePortal )

    def __init__( self, id ):
        self.id = id

    def __call__( self, content, skin_method_name ):
        " "
        sfx = self._skin_name_suffix
        return sfx and skin_method_name.endswith( sfx )

    security.declareProtected( ManagePortal, 'getTypeLabel' )
    def getTypeLabel( self ):
        " "
        return self.PREDICATE_TYPE

    security.declareProtected( ManagePortal, 'edit' )
    def edit( self, skin_name_suffix ):
        " "
        if skin_name_suffix!= self._skin_name_suffix:
            self._skin_name_suffix = skin_name_suffix

    security.declareProtected( ManagePortal, 'predicateWidget' )
    predicateWidget = DTMLFile( 'cpp_nameSuffixWidget', _dtmldir )

    def getSkinNameSuffix( self ):
        " "
        return self._skin_name_suffix or ''

InitializeClass( NameSuffixPredicate )
registerPredicateType( NameSuffixPredicate.PREDICATE_TYPE, NameSuffixPredicate )


class CachingTool( SimpleItem ):
    """
        Registry for rules which map content objects / skin names to
        cache managers.
    """
    meta_type = 'Core Caching Tool'
    id = 'portal_caching'

    manage_options = ( { 'label'    : 'Predicates'
                       , 'action'   : 'manage_predicates'
                       }
                     , #{ 'label'    : 'Test'
                       #, 'action'   : 'manage_testRegistry'
                       #}
                     ) + SimpleItem.manage_options

    security = ClassSecurityInfo()

    def __init__( self ):
        self._predicate_ids  = ()
        self._predicates     = PersistentMapping()

    #
    #   ZMI
    #
    security.declarePublic( 'listPredicateTypes' )
    def listPredicateTypes( self ):
        """
        """
        return map( lambda x: x[0], _predicate_types )

    security.declareProtected( ManagePortal, 'manage_predicates' )
    manage_predicates = DTMLFile( 'cpp_registryPredList', _dtmldir )

    security.declareProtected( ManagePortal, 'doAddPredicate' )
    def doAddPredicate( self, predicate_id, predicate_type, REQUEST ):
        """
        """
        self.addPredicate( predicate_id, predicate_type )
        REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
                              + '/manage_predicates'
                              + '?manage_tabs_message=Predicate+added.'
                              )

    security.declareProtected( ManagePortal, 'doUpdatePredicate' )
    def doUpdatePredicate( self
                         , predicate_id
                         , predicate
                         , cacheManagerID
                         , REQUEST
                         ):
        """
        """
        self.updatePredicate( predicate_id, predicate, cacheManagerID )
        REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
                              + '/manage_predicates'
                              + '?manage_tabs_message=Predicate+updated.'
                              )

    security.declareProtected( ManagePortal, 'doMovePredicateUp' )
    def doMovePredicateUp( self, predicate_id, REQUEST ):
        """
        """
        predicate_ids = list( self._predicate_ids )
        ndx = predicate_ids.index( predicate_id )
        if ndx == 0:
            msg = "Predicate+already+first."
        else:
            self.reorderPredicate( predicate_id, ndx - 1 )
            msg = "Predicate+moved."
        REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
                              + '/manage_predicates'
                              + '?manage_tabs_message=%s' % msg
                              )

    security.declareProtected( ManagePortal, 'doMovePredicateDown' )
    def doMovePredicateDown( self, predicate_id, REQUEST ):
        """
        """
        predicate_ids = list( self._predicate_ids )
        ndx = predicate_ids.index( predicate_id )
        if ndx == len( predicate_ids ) - 1:
            msg = "Predicate+already+last."
        else:
            self.reorderPredicate( predicate_id, ndx + 1 )
            msg = "Predicate+moved."
        REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
                              + '/manage_predicates'
                              + '?manage_tabs_message=%s' % msg
                              )

    security.declareProtected( ManagePortal, 'doRemovePredicate' )
    def doRemovePredicate( self, predicate_id, REQUEST ):
        """
        """
        self.removePredicate( predicate_id )
        REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
                              + '/manage_predicates'
                              + '?manage_tabs_message=Predicate+removed.'
                              )

#   security.declareProtected( ManagePortal, 'manage_testRegistry' )
#   manage_testRegistry = DTMLFile( 'registryTest', _dtmldir )
#
#   security.declareProtected( ManagePortal, 'doTestRegistry' )
#   def doTestRegistry( self, name, content_type, body, REQUEST ):
#       """
#       """
#       typeName = self.findTypeName( name, content_type, body )
#       if typeName is None:
#           typeName = '<unknown>'
#       REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
#                              + '/manage_testRegistry'
#                              + '?testResults=Type:%s'
#                                      % urllib.quote( typeName )
#                              )

    #
    #   Predicate manipulation
    #
    security.declarePublic( 'getPredicate' )
    def getPredicate( self, predicate_id ):
        """
            Find the predicate whose id is 'id';  return the predicate
            object, if found, or else None.
        """
        return self._predicates.get( predicate_id, ( None, None ) )[0]

    security.declarePublic( 'listPredicates' )
    def listPredicates( self ):
        """
            Return a sequence of tuples,
            '( id, ( predicate, cacheManagerID ) )'
            for all predicates in the registry 
        """
        result = []
        for predicate_id in self._predicate_ids:
            result.append( ( predicate_id, self._predicates[ predicate_id ] ) )
        return tuple( result )

    security.declarePublic( 'getTypeObjectName' )
    def getCacheManagerID( self, predicate_id ):
        """
            Find the predicate whose id is 'id';  return the id of
            the cache manager, if found, or else None.
        """
        return self._predicates.get( predicate_id, ( None, None ) )[1]

    security.declareProtected( ManagePortal, 'addPredicate' )
    def addPredicate( self, predicate_id, predicate_type ):
        """
            Add a predicate to this element of type 'typ' to the registry.
        """
        if predicate_id in self._predicate_ids:
            raise ValueError, "Existing predicate: %s" % predicate_id

        klass = None
        for key, value in _predicate_types:
            if key == predicate_type:
                klass = value

        if klass is None:
            raise ValueError, "Unknown predicate type: %s" % predicate_type

        self._predicates[ predicate_id ] = ( klass( predicate_id ), None )
        self._predicate_ids = self._predicate_ids + ( predicate_id, )

    security.declareProtected( ManagePortal, 'addPredicate' )
    def updatePredicate( self, predicate_id, predicate, cacheManagerID ):
        """
            Update a predicate in this element.
        """
        if not predicate_id in self._predicate_ids:
            raise ValueError, "Unknown predicate: %s" % predicate_id

        predObj = self._predicates[ predicate_id ][0]
        mapply( predObj.edit, (), predicate.__dict__ )
        self.assignCacheManagerID( predicate_id, cacheManagerID )

    security.declareProtected( ManagePortal, 'removePredicate' )
    def removePredicate( self, predicate_id ):
        """
            Remove a predicate from the registry.
        """
        del self._predicates[ predicate_id ]
        idlist = list( self._predicate_ids )
        ndx = idlist.index( predicate_id )
        idlist = idlist[ :ndx ] + idlist[ ndx+1: ]
        self._predicate_ids = tuple( idlist )

    security.declareProtected( ManagePortal, 'reorderPredicate' )
    def reorderPredicate( self, predicate_id, newIndex ):
        """
            Move a given predicate to a new location in the list.
        """
        idlist = list( self._predicate_ids )
        ndx = idlist.index( predicate_id )
        pred = idlist[ ndx ]
        idlist = idlist[ :ndx ] + idlist[ ndx+1: ]
        idlist.insert( newIndex, pred )
        self._predicate_ids = tuple( idlist )

    security.declareProtected( ManagePortal, 'CacheManagerID' )
    def assignCacheManagerID( self, predicate_id, cacheManagerID ):
        """
            Bind the given predicate to a particular cache manager.
        """
        pred, replaced = self._predicates[ predicate_id ]
        self._predicates[ predicate_id ] = ( pred, cacheManagerID )

    #
    #   portal_caching interface
    #
    def findCacheManagerID( self, content, skin_name ):
        """
            Perform a lookup over a collection of rules, returning the
            the cache manager object corresponding to content / skin_name,
            or None if no match found.
        """
        for predicate_id in self._predicate_ids:
            pred, cacheManagerID = self._predicates[ predicate_id ]
            if pred( content, skin_name ):
                return cacheManagerID

        return None

InitializeClass( CachingTool )

def manage_addCachingTool( self, REQUEST=None ):
    """
        Add a CachingTool to self.
    """
    id = CachingTool.id
    reg = CachingTool()
    self._setObject( id, reg )

    if REQUEST is not None:
        REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
                              + '/manage_main'
                              + '?manage_tabs_message=Caching+tool+added.'
                              )

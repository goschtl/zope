##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Unique Id Handler Tool

Provides support for accessing unique ids on content object.

$Id$
"""
__version__ = "$Revision$"

import Missing

import zLOG
from Globals import InitializeClass, Persistent
from AccessControl import ClassSecurityInfo
from Acquisition import Implicit, aq_base

from OFS.SimpleItem import SimpleItem

from Products.CMFCore.utils import getToolByName, UniqueObject
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.permissions import ManagePortal

from Products.CMFUid.interfaces import IUniqueIdHandler
from Products.CMFUid.interfaces import UniqueIdError

UID_ATTRIBUTE_NAME = 'cmf_uid'

class UniqueIdHandlerTool(UniqueObject, SimpleItem, ActionProviderBase):
    __doc__ = __doc__ # copy from module

    __implements__ = (
        SimpleItem.__implements__,
        IUniqueIdHandler,
    )

    id = 'portal_uidhandler'
    alternative_id = "portal_standard_uidhandler"
    meta_type = 'Unique Id Handler Tool'
    
    # make the uid attribute name available for the unit tests
    # not meant to be altered as long you don't know what you do!!!
    UID_ATTRIBUTE_NAME = UID_ATTRIBUTE_NAME
    
    # make the exception class available through the tool
    UniqueIdError = UniqueIdError
    
    security = ClassSecurityInfo()
    
    def _reindexObject(self, obj):
        # add uid index and colums to catalog if not yet done
        UID_ATTRIBUTE_NAME = self.UID_ATTRIBUTE_NAME
        catalog = getToolByName(self, 'portal_catalog')
        if UID_ATTRIBUTE_NAME not in catalog.indexes():
            catalog.addIndex(UID_ATTRIBUTE_NAME, 'FieldIndex')
            catalog.addColumn(UID_ATTRIBUTE_NAME)
        
        # reindex
        catalog.reindexObject(obj)

    security.declarePublic('queryUid')
    def queryUid(self, obj, default=None):
        """See IUniqueIdQuery.
        """
        uid = getattr(aq_base(obj), self.UID_ATTRIBUTE_NAME, None)
        # If 'obj' is a content object the 'uid' attribute is usually a
        # callable object. If 'obj' is a catalog brain the uid attribute 
        # is non callable and possibly equals the 'Missing.MV' value.
        if uid is Missing.MV:
            return default
        if callable(uid):
            return uid()
        return uid
    
    security.declarePublic('getUid')
    def getUid(self, obj):
        """See IUniqueIdQuery.
        """
        uid = self.queryUid(obj, None)
        if uid is None:
            raise UniqueIdError, "No unique id available on '%s'" % obj
        return uid
    
    
    security.declareProtected(ManagePortal, 'register')
    def register(self, obj):
        """See IUniqueIdSet.
        """
        uid = self.queryUid(obj, default=None)
        if uid is None:
            # attach a unique id annotation to the object
            anno_tool = getToolByName(self, 'portal_uidannotation')
            annotation = anno_tool(obj, self.UID_ATTRIBUTE_NAME)
            
            # initialize the annotation with a (new) unique id
            generator = getToolByName(self, 'portal_uidgenerator')
            uid = generator()
            annotation.setUid(uid)
            
            # reindex the object
            self._reindexObject(obj)
            
        return uid
    
    security.declareProtected(ManagePortal, 'unregister')
    def unregister(self, obj):
        """See IUniqueIdSet.
        """
        UID_ATTRIBUTE_NAME = self.UID_ATTRIBUTE_NAME
        if getattr(aq_base(obj), UID_ATTRIBUTE_NAME, None) is None:
            raise UniqueIdError, \
                  "No unique id available to be unregistered on '%s'" % obj
            
        # delete the uid and reindex
        delattr(obj, UID_ATTRIBUTE_NAME)
        self._reindexObject(obj)
    
    
    security.declarePublic('queryBrain')
    def queryBrain(self, uid, default=None):
        """See IUniqueIdBrainQuery.
        """
        if uid is None:
            return default
        
        catalog = getToolByName(self, 'portal_catalog')
        result = catalog({self.UID_ATTRIBUTE_NAME: uid})
        len_result = len(result)

        # return None if no object found with this uid
        if len_result == 0:
            return default

        # print a message to the log  if more than one object has
        # the same uid (uups!)
        # TODO: It would be nice if there were a logging tool :-)
        if len_result > 1:
            zLOG.LOG("CMUid ASSERT:", zLOG.INFO,
                     "Uups, %s objects have '%s' as uid!!!" % \
                     (len_result, uid))
        
        return result[0]
        
    security.declarePublic('getBrain')
    def getBrain(self, uid):
        """See IUniqueIdBrainQuery.
        """
        brain = self.queryBrain(obj, default=None)
        if brain is None:
            raise UniqueIdError, "No object found with '%s' as uid." % uid
        return brain
        
    security.declarePublic('queryObject')
    def queryObject(self, uid, default=None):
        """See IUniqueIdQuery.
        """
        brain = self.queryBrain(uid, default=default)
        if brain is default:
            return default
        return brain.getObject()
    
    security.declarePublic('getObject')
    def getObject(self, uid):
        """See IUniqueIdQuery.
        """
        brain = self.queryBrain(uid, default=None)
        if brain is None:
            raise UniqueIdError, "No object found with '%s' as uid." % uid
        return brain.getObject()
        
InitializeClass(UniqueIdHandlerTool)

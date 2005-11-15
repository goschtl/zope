from AccessControl import ClassSecurityInfo
from Products.ZCatalog.ZCatalog import ZCatalog

from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore import CMFCorePermissions

from utils import unique, make_uuid
from types import StringType, UnicodeType

from Globals import InitializeClass

from Referenceable import Referenceable
from reference_config import *

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import os

_www = os.path.join(os.path.dirname(__file__), 'www')

STRING_TYPES = (StringType, UnicodeType)



class UIDCatalog(UniqueObject, ZCatalog):
    id = UID_MANAGER
    security = ClassSecurityInfo()
    protect = security.declareProtected
    
    manage_options = ZCatalog.manage_options

    
    ### ## Public API
    def catalog_object(self, object, uid=None, idxs=None, update_metadata=1):
        """
        The UID catalog has the special requirement that UUID's
        while unique occur multiple times within the scope of its
        index and really belong to a tuple of elements that constuct
        the primary key. (Minimally version and possibly things like
        language)
        """
    

    def deleteReference(self, source, target, relationship=None):
        sID, sobj = self._uidFor(source)
        tID, tobj = self._uidFor(target)

        objects = self._resolveBrains(self._queryFor(sID, tID, relationship))
        if objects:
            self._deleteReference(objects[0])

    def deleteReferences(self, object, relationship=None):
        """delete all the references held by an object"""
        [self._deleteReference(b) for b in
         (self.getReferences(object) or []) +
         (self.getBackReferences(object) or [])]

    def getReferences(self, object, relationship=None):
        """return a collection of reference objects"""
        sID, sobj = self._uidFor(object)
        brains = self._queryFor(sid=sID, relationship=relationship)
        return self._resolveBrains(brains)

    def getBackReferences(self, object, relationship=None):
        """return a collection of reference objects"""
        # Back refs would be anything that target this object
        sID, sobj = self._uidFor(object)
        brains = self._queryFor(tid=sID, relationship=relationship)
        return self._resolveBrains(brains)

    def hasRelationshipTo(self, source, target, relationship):
        sID, sobj = self._uidFor(source)
        tID, tobj = self._uidFor(target)

        brains = self._queryFor(sID, tID, relationship)
        result = False
        if brains:
            referenceObject = brains[0].getObject()
            result = True

        return result

    def getRelationships(self, object):
        """Get all relationship types this object has to other objects"""
        sID, sobj = self._uidFor(object)
        brains = self._queryFor(sid=sID)
        res = {}
        for b in brains:
            res[b.relationship]=1

        return res.keys()


    def isReferenceable(self, object):
        #Check for the catalogAware interface, there is no marker
        return IReferenceable.isImplementedBy(object) or hasattr(object, 'isReferenceable')


    def reference_url(self, object):
        """return a url to an object that will resolve by reference"""
        sID, sobj = self._uidFor(object)
        return "%s/lookupObject?uuid=%s" % (self.absolute_url(), sID)

    def lookupObject(self, uuid):
        """Lookup an object by its uuid"""
        return self._objectByUUID(uuid)


    #####
    ## UID register/unregister
    protect('registerObject', CMFCorePermissions.ModifyPortalContent)
    def registerObject(self, object):
        self._uidFor(object)

    protect('unregisterObject', CMFCorePermissions.ModifyPortalContent)
    def unregisterObject(self, object):
        self.deleteReferences(object)
        

    ######
    ## Private/Internal
    def _objectByUUID(self, uuid):
        tool = getToolByName(self, UID_MANAGER)
        brains = tool(UID=uuid)
        if not brains:
            return None
        return brains[0].getObject()

    def _queryFor(self, sid=None, tid=None, relationship=None, targetId=None, merge=1):
        """query reference catalog for object matching the info we are
        given, returns brains

        Note: targetId is the actual id of the target object, not its UID
        """

        q = {}
        if sid: q['sourceUID'] = sid
        if tid: q['targetUID'] = tid
        if relationship: q['relationship'] = relationship
        if targetId: q['targetId'] = targetId
        brains = self.searchResults(q, merge=merge)

        return brains


    def _uidFor(self, object):
        # We should really check for the interface but I have an idea
        # about simple annotated objects I want to play out
        if type(object) not in STRING_TYPES:
            uobject = object.aq_base
            if not self.isReferenceable(object):
                raise ReferenceException

            if not getattr(uobject, UUID_ATTR, None):
                uuid = self._getUUIDFor(object)
            else:
                uuid = getattr(uobject, UUID_ATTR)
        else:
            uuid = object
            #and we look up the object
            uid_catalog = getToolByName(self, UID_MANAGER)
            brains = uid_catalog(UUID=uuid)
            object = brains[0].getObject()

        return uuid, object

    def _getUUIDFor(self, object):
        """generate and attach a new uid to the object returning it"""
        uuid = make_uuid(object.getId())
        setattr(object, UUID_ATTR, uuid)
        
        uc = getToolByName(self, UID_MANAGER)
        uc.catalog_object(object, '/'.join(object.getPhysicalPath()))

        return uuid

    def _deleteReference(self, referenceObject):
        try:
            referenceObject.delHook(self, referenceObject.getSourceObject(), referenceObject.getTargetObject())
        except ReferenceException:
            pass
        else:
            self.uncatalog_object(referenceObject.getId())
            self._delObject(referenceObject.getId())
            #We actually deleted the reference, we special case kill its uuid
            referenceObject._ref_unregister()

    def _resolveBrains(self, brains):
        objects = []
        if brains:
            objects = [b.getObject() for b in brains]
            objects = [b for b in objects if b]
        return objects

    def _makeName(self, *args):
        name = make_uuid(*args)
        name = "ref_%s" % name
        return name

def manage_addReferenceCatalog(self, id, title,
                               vocab_id=None, # Deprecated
                               REQUEST=None):
    """Add a ReferenceCatalog object
    """
    id=str(id)
    title=str(title)
    c=ReferenceCatalog(id, title, vocab_id, self)
    self._setObject(id, c)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST,update_menu=1)


InitializeClass(ReferenceCatalog)

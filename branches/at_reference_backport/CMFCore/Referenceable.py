from reference_config import *
from ExtensionClass import Base
from utils import getToolByName
from interfaces.referenceable import IReferenceable
from OFS.ObjectManager import BeforeDeleteException

class Referenceable(Base):

    __implements__ = IReferenceable
    isReferenceable = True
    
    # References
    # ----
    def UID(self):
        """return a uuid, getting one if absent"""
        return getattr(self, UUID_ATTR, self._uuid_register())
    
    def _uuid_register(self, reference_manager=None):
        """get a uuid that can be used for references"""
        uuid = getattr(self, UUID_ATTR, None)
        if uuid: return uuid
        
        if not reference_manager:
            reference_manager = getToolByName(self, REFERENCE_MANAGER, None)
           
        if reference_manager is not None:
            reference_manager.registerObject(self)

            uc = getattr(reference_manager, UID_MANAGER)
            uc.catalog_object(self, '/'.join(self.getPhysicalPath()))
        

    def _uuid_unregister(self, reference_manager=None):
        """remove all references"""
        if not reference_manager:
            reference_manager = getToolByName(self, REFERENCE_MANAGER, None)
            
        if reference_manager is not None:
            reference_manager.unregisterObject(self)

    # Reference Syntatic Sugar
    # ----
    def reference_url(self):
        """like absoluteURL, but return a link to the object with this UID"""
        tool = getToolByName(self, REFERENCE_MANAGER)
        return tool.reference_url(self)

    def hasRelationshipTo(self, target, relationship=None):
        tool = getToolByName(self, REFERENCE_MANAGER)
        return tool.hasRelationshipTo(self, target, relationship)

    def addReference(self, object, relationship=None, **kwargs):
        tool = getToolByName(self, REFERENCE_MANAGER)
        return tool.addReference(self, object, relationship, **kwargs)

    def deleteReference(self, target, relationship=None):
        tool = getToolByName(self, REFERENCE_MANAGER)
        return tool.deleteReference(self, target, relationship)

    def deleteReferences(self, relationship=None):
        tool = getToolByName(self, REFERENCE_MANAGER)
        return tool.deleteReferences(self, relationship)

    def getRelationships(self):
        """What kinds of relationships does this object have"""
        tool = getToolByName(self, REFERENCE_MANAGER)
        return tool.getRelationships(self)

    def getRefs(self, relationship=None):
        """get all the referenced objects for this object"""
        tool = getToolByName(self, REFERENCE_MANAGER)
        refs = tool.getReferences(self, relationship)
        if refs:
            return [ref.getTargetObject() for ref in refs]
        return []

    def getBRefs(self, relationship=None):
        """get all the back referenced objects for this object"""
        tool = getToolByName(self, REFERENCE_MANAGER)
        refs = tool.getBackReferences(self, relationship)
        if refs:
            return [ref.getSourceObject() for ref in refs]
        return []

    ## Hook Support
    def manage_afterAdd(self, item, container):
        """add hook"""
        self._uuid_register()

    def manage_afterClone(self, item):
        """copy hook"""
        setattr(self, UUID_ATTR, None)
        self._uuid_register()
    
    def manage_beforeDelete(self, item, container):
        """delete hook"""
        keepingRefsOnMove= getattr(self, KEEP_REFS_ON_MOVE, False)
        
        if keepingRefsOnMove is False:
            from ReferenceCatalog import ReferenceException
            ## This is an actual delete
            rc = getattr(self, REFERENCE_MANAGER)
            if not rc: return
            references = rc.getReferences(self)
            back_references = rc.getBackReferences(self)
            try:
                #First check the 'delete cascade' case
                if references:
                    for ref in references:
                        ref.beforeSourceDeleteInformTarget()
                        ref._uuid_unregister(rc)
                #Then check the 'holding/ref count' case
                if back_references:
                    for ref in back_references:
                        ref.beforeTargetDeleteInformSource()
                        ref._uuid_unregister(rc)
                self._uuid_unregister(rc)

            except ReferenceException, E:
                raise BeforeDeleteException(E)
            
        setattr(self, KEEP_REFS_ON_MOVE, False)

    def _notifyOfCopyTo(self, container, op=0):
        """keep reference info internally when op == 1 (move)
        because in those cases we need to keep refs"""
        if op==1:
            setattr(self, KEEP_REFS_ON_MOVE, True)





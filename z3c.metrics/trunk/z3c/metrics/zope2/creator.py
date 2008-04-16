from zope import interface, component
from zope.cachedescriptors import property

from Products.CMFCore import interfaces as cmf_ifaces
from Products.CMFCore import utils as cmf_utils

from z3c.metrics import interfaces

class CreatorLookup(object):
    interface.implements(interfaces.ICreatorLookup)
    component.adapts(cmf_ifaces.ICatalogableDublinCore)

    def __init__(self, context):
        self.portal_membership = cmf_utils.getToolByName(
            context, 'portal_membership')

    def __call__(self, creator_id):
        return self.portal_membership.getMemberById(creator_id)

class Creators(object):
    interface.implements(interfaces.ICreated)
    component.adapts(cmf_ifaces.ICatalogableDublinCore)

    def __init__(self, context):
        self.context = context

    @property.Lazy
    def creators(self):
        return self.context.listCreators()

    

from zope import interface, component
from zope.testing import cleanup
import zope.event
from zope.app.container import contained

import Acquisition

from Products.CMFCore import interfaces as cmf_ifaces
from Products.CMFCore import utils as cmf_utils
from Products.CMFDefault import DiscussionItem

from z3c.metrics import interfaces

class ReplyCreatedEvent(contained.ObjectAddedEvent):
    interface.implementsOnly(interfaces.IChangeScoreEvent,
                             interfaces.IAddValueEvent)

class ReplyDeletedEvent(contained.ObjectRemovedEvent):
    interface.implementsOnly(interfaces.IChangeScoreEvent,
                             interfaces.IRemoveValueEvent)
    
def createReply(self, *args, **kw):
    reply_id = createReply.orig(
        self, *args, **kw)
    zope.event.notify(ReplyCreatedEvent(
        object=self.getReply(reply_id), newParent=self,
        newName=reply_id))
    return reply_id
createReply.orig = DiscussionItem.DiscussionItemContainer.createReply
    
def deleteReply(self, reply_id, *args, **kw):
    reply = self.getReply(reply_id)
    reply_id = deleteReply.orig(self, reply_id, *args, **kw)
    zope.event.notify(ReplyDeletedEvent(
        object=reply, oldParent=self, oldName=reply_id))
    return reply_id
deleteReply.orig = DiscussionItem.DiscussionItemContainer.deleteReply

def patch():
    DiscussionItem.DiscussionItemContainer.createReply = createReply
    DiscussionItem.DiscussionItemContainer.deleteReply = deleteReply

def unpatch():
    DiscussionItem.DiscussionItemContainer.createReply = (
        createReply.orig)
    DiscussionItem.DiscussionItemContainer.deleteReply = (
        deleteReply.orig)

patch()
cleanup.addCleanUp(unpatch)

@component.adapter(cmf_ifaces.IDiscussionResponse,
                   interfaces.IChangeScoreEvent)
def dispatchToDiscussed(obj, event):
    parent = event.newParent
    if parent is None:
        parent = event.oldParent
    discussed = Acquisition.aq_parent(Acquisition.aq_inner(parent))
    for _ in component.subscribers(
        [obj, event, discussed], None):
        pass # Just make sure the handlers run

@component.adapter(cmf_ifaces.IDiscussable,
                   interfaces.IBuildScoreEvent)
def dispatchToReplies(obj, event, dispatched=None):
    portal_discussion = cmf_utils.getToolByName(
        obj, 'portal_discussion')
    if dispatched is None:
        # For creator dispatch
        dispatched = obj
    for reply in portal_discussion.getDiscussionFor(obj).getReplies():
        for _ in component.subscribers(
            [reply, event, dispatched], None):
            pass # Just make sure the handlers run
    

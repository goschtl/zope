##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""XML-RPC methods for the Bug Tracker and Bugs

XML-RPC might be the best method to support mail-input. 

$Id: xmlrpc.py,v 1.1 2003/07/28 10:21:06 srichter Exp $
"""
import base64

from zope.event import notify
from zope.app.publisher.xmlrpc import MethodPublisher
from zope.schema.vocabulary import getVocabularyRegistry

from zope.app import zapi
from zope.app.container.contained import contained
from zope.app.container.interfaces import INameChooser
from zope.app.event.objectevent import ObjectCreatedEvent, ObjectModifiedEvent
from zope.app.file import File, Image

from bugtracker.bug import Bug
from bugtracker.comment import Comment
from bugtracker.interfaces import IComment, IBugDependencies


class UnknownEncoding(Exception):
    """We specify encodings for the attachment data, since it is expected that
    they are often binary data. This exception is raised, if none of the
    available encodings was chosen."""
    

class BugTrackerMethods(MethodPublisher):
    """XML-RPC methods for the Bug Tracker object."""

    def getBugNames(self):
        """Get a list of all bugs."""
        return list(self.context.keys())
  
    def addBug(self, title, description, type=u'bug', status=u'new',
               priority=u'normal', release=u'None', owners=None,
               dependencies=None):
        """Add a message. Returns the id of the bug."""
        bug = Bug()
        bug.title = title
        bug.description = description
        bug.type = type
        bug.status = status
        bug.priority = priority
        bug.release = release
        if owners is not None:
            registry = getVocabularyRegistry()
            vocab = registry.get(self.context, 'Users')
            owner_ids = []
            for term in vocab:
                if term.principal['login'] in owners:
                    owner_ids.append(term.value)
            bug.owners = owner_ids
        if dependencies is not None:
            bug.dependencies = dependencies
        chooser = INameChooser(self.context)
        self.context[chooser.chooseName('', bug)] = bug
        return zapi.name(bug)
  
    def deleteBug(self, name):
        """Delete a bug. Return True, if successful."""
        self.context.__delitem__(name)
        return True 


class BugMethods(MethodPublisher):

    def getProperties(self):
        registry = getVocabularyRegistry()
        vocab = registry.get(self.context, 'Users')
        owners = map(lambda o: vocab.getTerm(o).principal['login'],
                     self.context.owners)        
        deps = IBugDependencies(self.context)
        return {'title' : self.context.title,
                'description' : self.context.description,
                'type' : self.context.type,
                'status' : self.context.status,
                'priority' : self.context.priority,
                'release' : self.context.release,
                'owners' : owners,
                'dependencies' : deps.dependencies
                }

    def setProperties(self, title=None, description=None, type=None,
                      status=None, priority=None, release=None,
                      owners=None, dependencies=None):
        """Set the properties of the bug."""
        bug = self.context
        if title is not None:
            bug.title = title
        if description is not None:
            bug.description = description
        if type is not None:
            bug.type = type
        if status is not None:
            bug.status = status
        if priority is not None:
            bug.priority = priority
        if release is not None:
            bug.release = release
        if owners is not None:
            registry = getVocabularyRegistry()
            vocab = registry.get(self.context, 'Users')
            owner_ids = []
            for term in vocab:
                if term.principal['login'] in owners:
                    owner_ids.append(term.value)
            bug.owners = owner_ids
        if dependencies is not None:
            deps = IBugDependencies(bug)
            deps.dependencies = dependencies
        notify(ObjectModifiedEvent(bug))
        return True

    def getCommentNames(self):
        """Get the names (ids) of the comments for this bug."""
        names = []
        for name, obj in self.context.items():
            if IComment.providedBy(obj):
                names.append(name)
        return names

    def addComment(self, body):
        """Add a comment to the bug."""
        comment = Comment()
        comment.body = body
        names = filter(lambda n: n.startswith('comment'), self.context.keys())
        int_names = map(lambda n: int(n[7:]), names)
        name = 'comment1'
        if int_names:
            name = 'comment' + str(max(int_names)+1)
        self.context[name] = comment
        return zapi.name(comment)

    def deleteComment(self, name):
        """Delete a Comment. Return True, if successful."""
        self.context.__delitem__(name)
        return True 

    def getAttachmentNames(self):
        """Get the names (ids) of the attachments for this bug."""
        namess = []
        for name, obj in self.context.items():
            if not IComment.providedBy(obj):
                names.append(name)
        return names

    def addAttachment(self, name, data, type="File", encoding="base64"):
        """Add an attachment to the bug."""
        if type == 'Image':
            attach = Image()
        else:
            attach = File()
        if encoding == 'base64':
            attach.data = base64.decodestring(data)
        else:
            raise UnknownEncoding, 'The encoding is not known: %s' %encoding
        attach = contained(attach, self.context, name=name)
        self.context[name] = attach
        return zapi.name(attach)

    def deleteAttachment(self, name):
        """Delete an Attachment. Return True, if successful."""
        self.context.__delitem__(name)
        return True 


class CommentMethods(MethodPublisher):
    """XML-RPC Methods for a Bug Comment object."""

    def getBody(self):
        """Get the contents/body of the comment."""
        return self.context.body

    def setBody(self, body):
        """Give the comment new contents.""" 
        self.context.body = body
        return True


class AttachmentMethods(MethodPublisher):
    """XML-RPC Methods for Bug Attachments."""

    def getData(self, encoding='base64'):
        """Return the data of the attachment in the specified encoding."""
        if encoding == 'base64':
            return base64.encodestring(self.context.data)
        else:
            raise UnknownEncoding, 'The encoding is not known: %s' %encoding 

    def setData(self, data, encoding='base64'):
        """Set the data of the attachment converting from the specified
        encoding."""
        if encoding == 'base64':
            self.context.data = base64.decodestring(data)
        else:
            raise UnknownEncoding, 'The encoding is not known: %s' %encoding 

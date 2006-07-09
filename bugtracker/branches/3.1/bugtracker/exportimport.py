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
"""XML Import/Export facility

$Id: exportimport.py,v 1.6 2003/08/29 22:59:52 srichter Exp $
"""
VERSION = '1.0'

import base64
from xml.sax import parse
from xml.sax.handler import ContentHandler

from zope.i18n.locales import locales
from zope.publisher.browser import TestRequest
from zope.schema.vocabulary import getVocabularyRegistry
from zope.security.proxy import removeSecurityProxy 

from zope.app import zapi
from zope.app.dublincore.interfaces import IZopeDublinCore
from zope.app.file import File, Image
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from bugtracker.bug import Bug
from bugtracker.comment import Comment
from bugtracker.interfaces import IBugDependencies, IComment
from bugtracker.renderable import RenderableText


def _getPrincipalIdsByLogin(logins, vocab=None):
    """Convert logins to principal id.

    If no principal is found for a login, simply return the login name for
    this entry. This way not all users must exist.
    """
    if vocab is None:
        registry = getVocabularyRegistry()
        vocab = registry.get(None, 'Users')

    ids = []
    for login in logins:
        for term in vocab:
            if term.principal['login'] == login:
                ids.append(unicode(term.value))
                break
        else:
            ids.append(unicode(login))

    return ids
    

class XMLExport:

    template = ViewPageTemplateFile('template.xml')

    def __init__(self, tracker):
        self.context = tracker
        self.request = TestRequest()

    def getXML(self):
        return self.template()

    def title(self):
        return self.context.title        

    def version(self):
        return VERSION

    def vocabularies(self):
        registry = getVocabularyRegistry()
        vocabs = []
        for name in ('Stati', 'Priorities', 'BugTypes', 'Releases'):
            vocab = registry.get(self.context, name)
            vocabs.append({'name': name,
                           'terms' : iter(vocab),
                           'default' : vocab.default})
        return vocabs

    def bugs(self):
        return map(lambda item: BugInfo(item[0], item[1]), self.context.items())
            

class BugInfo:

    def __init__(self, name, bug):
        self.context = bug
        self.name = name
        self.locale = locales.getLocale('en')

    def id(self):
        return self.name

    def title(self):
        return self.context.title
        
    def description(self):
        return '\n'+self.context.description+'\n      '

    def description_ttype(self):
        return getattr(self.context.description, 'ttype',
                       'zope.source.plaintext')

    def submitter(self):
        registry = getVocabularyRegistry()
        vocab = registry.get(self.context, 'Users')
        try:
            return vocab.getTerm(self.context.submitter).principal['login']
        except LookupError:
            return self.context.submitter
        
    def created(self):
        dc = IZopeDublinCore(self.context)
        return self.locale.dates.getFormatter('dateTime', 'medium').format(
            dc.created)

    def modified(self):
        dc = IZopeDublinCore(self.context)
        if dc.modified is None:
            return self.created()
        return self.locale.dates.getFormatter('dateTime', 'medium').format(
            dc.modified)

    def status(self):
        return self.context.status

    def type(self):        
        return self.context.type

    def release(self):
        return self.context.release

    def priority(self):
        return self.context.priority

    def owners(self):
        # Principal ids are totally useless for exporting; use logins instead
        registry = getVocabularyRegistry()
        vocab = registry.get(self.context, 'Users')
        owners = []
        for owner in self.context.owners:
            try:
                owners.append(vocab.getTerm(owner).principal['login'])
            except LookupError:
                owners.append(owner)
        return ', '.join(owners)

    def dependencies(self):
        deps = IBugDependencies(self.context)
        return ", ".join(deps.dependencies)

    def comments(self):
        comments = []
        for name, obj in self.context.items():
            if IComment.providedBy(obj):
                comments.append(CommentInfo(name, obj))
        return comments
        
    def attachments(self):
        attachs = []
        for name, obj in self.context.items():
            if not IComment.providedBy(obj):
                attachs.append(AttachmentInfo(name, obj))
        return attachs
    

class CommentInfo:

    def __init__(self, name, comment):
        self.context = comment
        self.name = name
        self.locale = locales.getLocale('en')

    def id(self):
        return self.name

    def body(self):
        return '\n'+self.context.body+'\n        '

    def ttype(self):
        return getattr(self.context.body, 'ttype', 'zope.source.plaintext')

    def creator(self):
        dc = IZopeDublinCore(self.context)
        registry = getVocabularyRegistry()
        vocab = registry.get(self.context, 'Users')
        return vocab.getTerm(dc.creators[0]).principal['login']
        
    def created(self):
        dc = IZopeDublinCore(self.context)
        return self.locale.dates.getFormatter('dateTime', 'medium').format(
            dc.created)


class AttachmentInfo:

    def __init__(self, name, attach):
        self.context = attach
        self.name = name
        self.locale = locales.getLocale('en')

    def id(self):
        return self.name

    def type(self):
        if isinstance(self.context, Image):
            return 'Image'
        return 'File'
    
    def data(self):
        return base64.encodestring(self.context.data)

    def creator(self):
        dc = IZopeDublinCore(self.context)
        registry = getVocabularyRegistry()
        vocab = registry.get(self.context, 'Users')
        return vocab.getTerm(dc.creators[0]).principal['login']
        
    def created(self):
        dc = IZopeDublinCore(self.context)
        return self.locale.dates.getFormatter('dateTime', 'medium').format(
            dc.created)


class XMLImporter(ContentHandler):

    def __init__(self, context, encoding='latin-1'):
        self.context = context
        self.encoding = encoding
        self.locale = locales.getLocale('en')
        self.parser = self.locale.dates.getFormatter('dateTime', 'medium')
        self.chars = u''

    def startElement(self, name, attrs):
        handler = getattr(self, 'start' + name.title().replace('-', ''), None)
        if not handler:
            raise ValueError, 'Unknown element %s' % name

        handler(attrs)

    def endElement(self, name):
        handler = getattr(self, 'end' + name.title().replace('-', ''), None)
        if handler:
            handler()


    def characters(self, content):
        self.chars += content

    def noop(*args):
        pass

    startVocabularies = noop
    startBugs = noop
    startComments = noop
    startAttachments = noop
    
    def startBugtracker(self, attrs):
        assert attrs.get('version') == VERSION
        self.context.title = attrs.get('title')

    def startVocabulary(self, attrs):
        self.vocab_name = attrs.get('name', None)

    def endVocabulary(self):
        self.vocab_name = None

    def startTerm(self, attrs):
        registry = getVocabularyRegistry()
        vocab = registry.get(self.context, self.vocab_name)
        # TODO: I do not understand why my security does not work here.
        vocab = removeSecurityProxy(vocab)
        vocab.add(attrs.get('value'), attrs.get('title'))
        if attrs.get('default', None) is not None:
            vocab.default = attrs.get('value')

    def startBug(self, attrs):
        registry = getVocabularyRegistry()
        vocab = registry.get(self.context, 'Users')

        bug = Bug()
        bug.title = attrs.get('title')
        bug.status = attrs.get('status')
        bug.priority = attrs.get('priority')
        bug.type = attrs.get('type')
        bug.release = attrs.get('release')

        logins = attrs.get('owners').split(', ')
        logins = [login for login in logins if login.strip() != u'']
        bug.owners = _getPrincipalIdsByLogin(logins)

        deps_adapter = IBugDependencies(bug)
        deps = attrs.get('dependencies').split(', ')
        deps_adapter.setDependencies(filter(lambda o: o.strip() != u'', deps))
        dc = IZopeDublinCore(bug)
        dc.created = self.parser.parse(attrs.get('created'))
        dc.modified = self.parser.parse(attrs.get('modified'))
        dc.creators = _getPrincipalIdsByLogin([attrs.get('submitter')])
        self.bug = bug
        self.bug_name = attrs.get('id')

    def endBug(self):
        self.context[self.bug_name] = self.bug
        
    def startDescription(self, attrs):
        self.chars = u''
        self.description_ttype = attrs.get('ttype', 'zope.source.plaintext')

    def endDescription(self):
        self.bug.description = RenderableText(self.chars.strip(),
                                              self.description_ttype)

    def startComment(self, attrs):
        self.chars = u''
        comment = Comment()
        dc = IZopeDublinCore(comment)
        dc.created = self.parser.parse(attrs.get('created'))
        dc.creators = _getPrincipalIdsByLogin([attrs.get('creator')])
        self.comment = comment
        self.comment_name = attrs.get('id')
        self.comment_ttype = attrs.get('ttype', 'zope.source.plaintext')

    def endComment(self):
        self.comment.body = RenderableText(self.chars.strip(),
                                           self.comment_ttype)
        self.bug[self.comment_name] = self.comment

    def startAttachment(self, attrs):
        self.chars = u''
        type = attrs.get('type')
        if type == 'Image':
            attach = Image()
        else:
            attach = File()
        dc = IZopeDublinCore(attach)
        dc.created = self.parser.parse(attrs.get('created'))
        dc.creators = _getPrincipalIdsByLogin([attrs.get('creator')])
        self.attach = attach
        self.attach_name = attrs.get('id')

    def endAttachment(self):
        self.attach.data = base64.decodestring(self.chars.strip(' '))
        self.bug[self.attach_name] = self.attach


class XMLImport:

    def __init__(self, tracker):
        self.context = tracker

    def processXML(self, xml):
        parse(xml, XMLImporter(self.context))

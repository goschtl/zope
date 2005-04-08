##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Implementation of an Online Help Topic.


$Id$
"""
__docformat__ = 'restructuredtext'

import os

from persistent import Persistent
from zope.interface import implements
from zope.configuration.exceptions import ConfigurationError

from zope.app.container.sample import SampleContainer
from zope.app.content_types import guess_content_type
from zope.app.file.image import getImageInfo

from zope.app.onlinehelp.interfaces import IOnlineHelpTopic
from zope.app.onlinehelp.interfaces import ISourceTextOnlineHelpTopic
from zope.app.onlinehelp.interfaces import IRESTOnlineHelpTopic
from zope.app.onlinehelp.interfaces import ISTXOnlineHelpTopic
from zope.app.onlinehelp.interfaces import IZPTOnlineHelpTopic
from zope.app.onlinehelp.interfaces import IOnlineHelpResource


class OnlineHelpResource(Persistent):
    """
    Represents a resource that is used inside
    the rendered Help Topic - for example a screenshot.

    >>> from zope.app.onlinehelp.tests.test_onlinehelp import testdir
    >>> path = os.path.join(testdir(), 'test1.png')

    >>> resource = OnlineHelpResource(path)
    >>> resource.contentType
    'image/png'
    >>> resource._fileMode
    'rb'

    
    >>> path = os.path.join(testdir(), 'help2.txt')

    >>> resource = OnlineHelpResource(path)
    >>> resource.contentType
    'text/plain'
    >>> resource._fileMode
    'r'
    
    """
    implements(IOnlineHelpResource)

    def __init__(self, path='', contentType=''):
        self.path = path
        _data = open(os.path.normpath(self.path), 'rb').read()
        self._size=len(path)
        self._fileMode = 'rb'

        if contentType=='':
            content_type, encoding = guess_content_type(self.path, _data, '')
        if content_type.startswith('image/'):
            self.contentType, width, height = getImageInfo(_data)
        else:
            self.contentType = content_type

        if self.contentType.startswith('text/'):
            self._fileMode = 'r'

    def _getData(self):
        return open(os.path.normpath(self.path), self._fileMode).read()

    data = property(_getData)

    def getSize(self):
        '''See IFile'''
        return self._size


class BaseOnlineHelpTopic(SampleContainer):
    """
    Base class for custom Help Topic implementations.
    
    >>> from zope.app.onlinehelp.tests.test_onlinehelp import testdir
    >>> path = os.path.join(testdir(), 'help.txt')

    Create a Help Topic from a file
    
    >>> topic = BaseOnlineHelpTopic('help','Help',path,'')

    Test the title
    
    >>> topic.title
    'Help'

    Test the topic path
    >>> topic.getTopicPath()
    'help'
    >>> topic.parentPath = 'parent'
    >>> topic.getTopicPath()
    'parent/help'

    Resources can be added to an online help topic.
    >>> topic.addResources(['test1.png', 'test2.png'])
    >>> topic['test1.png'].contentType
    'image/png'
    >>> topic['test2.png'].contentType
    'image/png'
    """

    id = u""
    title = u""
    path = u""
    parentPath = u""
    interface = None
    view = None
    
    def __init__(self, id, title, path, parentPath, interface=None, view=None):
        """Initialize object."""
        self.id = id
        self.parentPath = parentPath
        self.title = title
        self.path = path
        self.interface = interface
        self.view = view

        if not os.path.exists(self.path):
            raise ConfigurationError(
                "Help Topic definition %s does not exist" % self.path
                )

        super(BaseOnlineHelpTopic, self).__init__()

    def addResources(self, resources):
        """ see IOnlineHelpTopic """
        dirname = os.path.dirname(self.path)
        for resource in resources:
            resource_path=dirname+'/'+resource
            if os.path.exists(resource_path):
                self[resource] = OnlineHelpResource(resource_path)

    def getTopicPath(self):
        """ see IOnlineHelpTopic """
        if self.parentPath:
            return self.parentPath+'/'+self.id
        else:
            return self.id

    def getSubTopics(self):
        res = []
        for item in self.values():
            if IOnlineHelpTopic.providedBy(item):
                res.append(item)
        
        return res


class SourceTextOnlineHelpTopic(BaseOnlineHelpTopic):
    """Source text methods mixin class."""

    type = None

    def _getSource(self):
        return open(os.path.normpath(self.path)).read()

    source = property(_getSource)


class OnlineHelpTopic(SourceTextOnlineHelpTopic, SampleContainer):
    """
    Represents a Help Topic. This generic implementation uses the filename
    extension for guess the type. This topic implementation supports plain
    text topics, restructured and structured text topics. HTML topics get 
    rendered as structured text. If a file doesn't have the right file 
    extension, use a explicit topic class for representing the right format.
    
    >>> from zope.app.onlinehelp.tests.test_onlinehelp import testdir
    >>> path = os.path.join(testdir(), 'help.txt')

    Create a Help Topic from a file
    
    >>> topic = OnlineHelpTopic('help','Help',path,'')

    Test the title
    
    >>> topic.title
    'Help'

    Test the topic path
    >>> topic.getTopicPath()
    'help'
    >>> topic.parentPath = 'parent'
    >>> topic.getTopicPath()
    'parent/help'

    The type should be set to plaintext, since
    the file extension is 'txt'
    
    >>> topic.type
    'zope.source.plaintext'

    Test the help content.

    >>> topic.source
    'This is a help!'

    >>> path = os.path.join(testdir(), 'help.stx')
    >>> topic = OnlineHelpTopic('help','Help',path,'')

    The type should now be structured text
    >>> topic.type
    'zope.source.stx'

    HTML files are treated as structured text files
    >>> path = os.path.join(testdir(), 'help.html')
    >>> topic = OnlineHelpTopic('help','Help',path,'')

    The type should still be structured text
    >>> topic.type
    'zope.source.stx'

    >>> path = os.path.join(testdir(), 'help.rst')
    >>> topic = OnlineHelpTopic('help','Help',path,'')

    The type should now be restructured text
    >>> topic.type
    'zope.source.rest'

    Resources can be added to an online help topic.
    >>> topic.addResources(['test1.png', 'test2.png'])
    >>> topic['test1.png'].contentType
    'image/png'
    >>> topic['test2.png'].contentType
    'image/png'
    """

    implements(ISourceTextOnlineHelpTopic)

    def __init__(self, id, title, path, parentPath, interface=None, view=None):
        """Initialize object."""
        super(OnlineHelpTopic, self).__init__(id, title, path, parentPath, 
              interface, view)

        filename = os.path.basename(path.lower())
        file_ext = 'txt'
        if len(filename.split('.'))>1:
            file_ext = filename.split('.')[-1]

        self.type = 'zope.source.plaintext'

        if file_ext in ('rst', 'rest') :
            self.type = 'zope.source.rest'
        elif file_ext in ('stx', 'html', 'htm'):
            self.type = 'zope.source.stx'


class RESTOnlineHelpTopic(SourceTextOnlineHelpTopic):
    """
    Represents a restructed text based Help Topic which has other 
    filename extension then '.rst' or 'rest'.
    
    >>> from zope.app.onlinehelp.tests.test_onlinehelp import testdir
    >>> path = os.path.join(testdir(), 'help.rst')

    Create a Help Topic from a file
    
    >>> topic = RESTOnlineHelpTopic('help','Help',path,'')

    Test the title
    
    >>> topic.title
    'Help'

    Test the topic path
    >>> topic.getTopicPath()
    'help'
    >>> topic.parentPath = 'parent'
    >>> topic.getTopicPath()
    'parent/help'

    The type should be set to rest, since the file extension is 'rest'
    
    >>> topic.type
    'zope.source.rest'

    Test the help content.

    >>> topic.source
    'This is a ReST help!'

    Resources can be added to an online help topic.
    >>> topic.addResources(['test1.png', 'test2.png'])
    >>> topic['test1.png'].contentType
    'image/png'
    >>> topic['test2.png'].contentType
    'image/png'
    """

    implements(IRESTOnlineHelpTopic)

    type = 'zope.source.rest'
    
    def __init__(self, id, title, path, parentPath, interface=None, view=None):
        """Initialize object."""
        super(RESTOnlineHelpTopic, self).__init__(id, title, path, parentPath, 
              interface, view)


class STXOnlineHelpTopic(SourceTextOnlineHelpTopic):
    """
    Represents a restructed text based Help Topic which has other 
    filename extension then '.stx'.
    
    >>> from zope.app.onlinehelp.tests.test_onlinehelp import testdir
    >>> path = os.path.join(testdir(), 'help.stx')

    Create a Help Topic from a file
    
    >>> topic = STXOnlineHelpTopic('help','Help',path,'')

    Test the title
    
    >>> topic.title
    'Help'

    Test the topic path
    >>> topic.getTopicPath()
    'help'
    >>> topic.parentPath = 'parent'
    >>> topic.getTopicPath()
    'parent/help'

    The type should be set to stx, since the file extension is 'stx'
    
    >>> topic.type
    'zope.source.stx'

    Test the help content.

    >>> topic.source
    'This is a STX help!'

    Resources can be added to an online help topic.
    >>> topic.addResources(['test1.png', 'test2.png'])
    >>> topic['test1.png'].contentType
    'image/png'
    >>> topic['test2.png'].contentType
    'image/png'
    """

    implements(ISTXOnlineHelpTopic)
    
    type = 'zope.source.stx'
    
    def __init__(self, id, title, path, parentPath, interface=None, view=None):
        """Initialize object."""
        super(STXOnlineHelpTopic, self).__init__(id, title, path, parentPath, 
              interface, view)


class ZPTOnlineHelpTopic(BaseOnlineHelpTopic):
    """
    Represents a page template based Help Topic which has other 
    filename extension then '.pt'.
    
    
    >>> from zope.publisher.browser import TestRequest
    >>> from zope.app.publisher.browser import BrowserView
    >>> from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
    >>> from zope.app.onlinehelp.tests.test_onlinehelp import testdir
    >>> path = os.path.join(testdir(), 'help.pt')

    Create a page template bsed Help Topic from a file
    
    >>> topic = ZPTOnlineHelpTopic('help','Help',path,'')

    Test the title
    
    >>> topic.title
    'Help'

    Test the topic path
    >>> topic.getTopicPath()
    'help'
    >>> topic.parentPath = 'parent'
    >>> topic.getTopicPath()
    'parent/help'

    Test the help content.

    >>> class TestView(BrowserView):
    ...     def index(self):
    ...         path = self.context.path
    ...         view = ViewPageTemplateFile(path)
    ...         return view(self)
    >>> request = TestRequest()
    >>> view = TestView(topic, request)
    >>> res = view.index()
    >>> str(res).find('<body>This is a ZPT help!</body>') > 0
    True

    Resources can be added to an online help topic.

    >>> topic.addResources(['test1.png', 'test2.png'])
    >>> topic['test1.png'].contentType
    'image/png'
    >>> topic['test2.png'].contentType
    'image/png'
    """

    implements(IZPTOnlineHelpTopic)

    def __init__(self, id, title, path, parentPath, interface=None, view=None):
        """Initialize object."""
        super(ZPTOnlineHelpTopic, self).__init__(id, title, path, parentPath, 
              interface, view)


def OnlineHelpTopicFactory(name, schema, label, permission, layer,
                    template, default_template, bases, for_, fields,
                    fulledit_path=None, fulledit_label=None, menu=u''):
    class_ = SimpleViewClass(template, used_for=schema, bases=bases)
    class_.schema = schema
    class_.label = label
    class_.fieldNames = fields

    class_.fulledit_path = fulledit_path
    if fulledit_path and (fulledit_label is None):
        fulledit_label = "Full edit"

    class_.fulledit_label = fulledit_label

    class_.generated_form = ViewPageTemplateFile(default_template)

    defineChecker(class_,
                  NamesChecker(("__call__", "__getitem__",
                                "browserDefault", "publishTraverse"),
                               permission))
    if layer is None:
        layer = IDefaultBrowserLayer

    s = zapi.getGlobalService(zapi.servicenames.Adapters)
    s.register((for_, layer), Interface, name, class_)



import sys
from zope.app.publisher.browser import BrowserView
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.publisher.interfaces import NotFound
from zope.interface import implements

class simple(BrowserView):

    implements(IBrowserPublisher)

    def browserDefault(self, request):
        return self, ()

    def publishTraverse(self, request, name):
        if name == 'index.html':
            return self.index

        raise NotFound(self, name, request)

    # XXX: we need some unittests for this !!!
    def __getitem__(self, name):
        return self.index.macros[name]

    def __call__(self, *args, **kw):
        return self.index(*args, **kw)

def SimpleViewClass(src, offering=None, used_for=None, bases=()):
    if offering is None:
        offering = sys._getframe(1).f_globals

    bases += (simple, )

    class_ = type("SimpleViewClass from %s" % src, bases,
                  {'index': ViewPageTemplateFile(src, offering)})

    if used_for is not None:
        class_.__used_for__ = used_for

    return class_


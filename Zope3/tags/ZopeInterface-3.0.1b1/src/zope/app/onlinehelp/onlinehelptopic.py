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

from zope.app.onlinehelp.interfaces import IOnlineHelpTopic, \
     IOnlineHelpResource


class OnlineHelpResource(Persistent):
    """
    Represents a resource that is used inside
    the rendered Help Topic - for example a screenshot.

    >>> from zope.app.onlinehelp.tests.test_onlinehelp import testdir
    >>> path = os.path.join(testdir(), 'test1.png')

    >>> resource = OnlineHelpResource(path)
    >>> resource.contentType
    'image/png'
    
    """
    implements(IOnlineHelpResource)

    def __init__(self, path='', contentType=''):
        self.path = path
        _data = open(os.path.normpath(self.path), 'rb').read()
        self._size=len(path)

        if contentType=='':
            content_type, encoding = guess_content_type(self.path, _data, '')
        if content_type.startswith('image/'):
            self.contentType, width, height = getImageInfo(_data)
        else:
            self.contentType = content_type

    def _getData(self):
        return open(os.path.normpath(self.path)).read()

    data = property(_getData)

    def getSize(self):
        '''See IFile'''
        return self._size


class OnlineHelpTopic(SampleContainer):
    """
    Represents a Help Topic.
    
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
    implements(IOnlineHelpTopic)

    def __init__(self, id, title, path, parentPath, interface=None, view=None):
        """Initialize object."""
        self.id = id
        self.parentPath = parentPath
        self.title = title
        self.path = path
        self.interface = interface
        self.view = view

        filename = os.path.basename(path.lower())
        file_ext = 'txt'
        if len(filename.split('.'))>1:
            file_ext = filename.split('.')[-1]

        self.type = 'zope.source.plaintext'

        if file_ext in ('rst', 'rest') :
            self.type = 'zope.source.rest'
        elif file_ext == 'stx':
            self.type = 'zope.source.stx'
        elif file_ext in ('html', 'htm'):
            self.type = 'zope.source.stx'

        if not os.path.exists(self.path):
            raise ConfigurationError(
                "Help Topic definition %s does not exist" % self.path
                )

        super(OnlineHelpTopic, self).__init__()

    id = u""

    parentPath = u""

    title = u""

    path = u""

    type = None

    interface = None

    view = None

    def _getSource(self):
        return open(os.path.normpath(self.path)).read()

    source = property(_getSource)

    def addResources(self, resources):
        """ see IOnlineHelpTopic """
        dirname = os.path.dirname(self.path)
        for resource in resources:
            resource_path=dirname+'/'+resource
            if os.path.exists(resource_path):
                self[resource] = OnlineHelpResource(resource_path)

    def getTopicPath(self):
        """ see IOnlineHelpTopic """
        if self.parentPath != '':
            return self.parentPath+'/'+self.id
        else:
            return self.id
                

##############################################################################
#
# Copyright (c) 2003-2004 Kupu Contributors. All rights reserved.
#
# This software is distributed under the terms of the Kupu
# License. See LICENSE.txt for license text. For a list of Kupu
# Contributors see CREDITS.txt.
#
##############################################################################
"""Zope3 isar sprint sample integration

$Id: app.py 6924 2004-10-14 09:57:19Z rineichen $
"""

import re
from zope.interface import implements

from zope.app.container.interfaces import IContainer
from zope.app.file.interfaces import IImage

from zorg.kupusupport.interfaces import IImageReadContainer
from zorg.kupusupport.interfaces import IKupuPolicy

options = re.DOTALL |  re.IGNORECASE

def html_body(html) :
    output = re.compile('<body.*?>(.*?)</body>', options).findall(html)
    if len(output) > 1 :
        print "Warning: more than one body tag."
    elif len(output) == 0 :     # hmmh, a html fragment?
        return html  
    return output[0]

def get_title(html) :
    output = re.compile('<title.*?>(.*?)</title>', options).findall(html)
    if len(output) > 1 :
        print "Warning: more than one title tag."
    elif len(output) == 0 :
        return None
    return output[0]
    
def get_description(html) :
    output = re.compile('<meta name="description" content="(.*?)".*?/>', options).findall(html)
    if len(output) > 1 :
        print "Warning: more than one description tag."
    elif len(output) == 0 :
        return None 
    return output[0]
    
    
class KupuEditableFile(object) :
    """ An adapter that implements the IKupuPolicy for
        regular file objects.
    """
    
    implements(IKupuPolicy)
    
    def __init__(self, context) :
        self.context = context
        
        
    def update(self, content, contentType="text/html", asContentType=None):
        """Update the content object using the editor output.
        
           contentType describes the provided content
           targetContentType prescribes in which format the content should be
           saved.

        """
        if asContentType is None :
            asContentType = self.context.contentType
        else :
            self.context.contentType = targetContentType
            
        assert contentType in "text/html", "text/plain"
        
        if asContentType == "text/html" :
            data = RestToHTML(content)
        elif asContentType == "text/plain" :
            data = content
            
        self.context.data = data
            
            
    def display(self, asContentType=None):
        """Display the specific editor content as text/html
           or rest text/plain
        """
        
        if asContentType is None :
            asContentType = self.context.contentType
         
        assert asContentType in "text/html", "text/plain"
        
        if asContentType == "text/html" :
        
            if self.context.contentType == "text/html" :
                return unicode(html_body(self.context.data), encoding="utf-8")
                
            if self.context.contentType == "text/plain" :
                return RestToHTML(self.context.data)
                
        elif asContentType == "text/plain" :
        
            if self.context.contentType == "text/html" :
                return HTMLToRest(html_body(self.context.data))
            if self.context.contentType == "text/plain" :
                return self.context.data   
        
        


class ImageReadContainer(object):
    """Provide IImage containment

    Create a container for example a kupu sample::

        >>> from zorg.kupusupport.sample.app import KupuSample
        >>> content = KupuSample()

    You can adapt the kupu sample content to IImageReadContainer using
    ImageReadContainer adapter::

        >>> container = ImageReadContainer(content)

    The behavior of an empty container is listed here::

        >>> container['image']
        Traceback (most recent call last):
        ...
        KeyError: 'image'
        >>> container.get('image', None)
        >>> container.__contains__('image')
        False
        >>> container.keys()
        []
        >>> iterator = iter(container)
        >>> iterator.next()
        Traceback (most recent call last):
        ...
        StopIteration
        >>> [value.__name__ for value in container.values()]
        []
        >>> [(key, value.__name__) for key, value in container.items()]
        []
        >>> len(container)
        0

    The behavior of none empty container is listed here::
        
        >>> from zope.app.file.image import Image
        >>> from zope.app.file.file import File
        >>> content[u'image'] = Image()
        >>> content[u'file'] = File()

        >>> container['image'].__name__
        u'image'
        >>> container['file']
        Traceback (most recent call last):
        ...
        KeyError: 'file'
        >>> container.get('image', None).__name__
        u'image'
        >>> container.get('file', None)
        >>> container.__contains__('image')
        True
        >>> container.__contains__('file')
        False
        >>> container.keys()
        [u'image']
        >>> iterator = iter(container)
        >>> key, value = iterator.next()
        >>> key, value.__name__
        (u'image', u'image')
        >>> iterator.next()
        Traceback (most recent call last):
        ...
        StopIteration
        >>> [value.__name__ for value in container.values()]
        [u'image']
        >>> [(key, value.__name__) for key, value in container.items()]
        [(u'image', u'image')]
        >>> len(container)
        1

    """

    implements(IImageReadContainer)

    __used_for__ = IContainer

    def __init__(self, context):
        self.context = context

    # private resources
    def _getContainer(self):
        # try to adapt the context to IContainer
        try:
            container = IContainer(self.context, None)
        except:
            container = None

        return container

    # adaption of zope.interface.common.mapping.IItemMapping
    def __getitem__(self, key):
        # private resources
        container = self._getContainer()

        # preconditions
        if container is None:
            raise KeyError(key)

        # essentials
        image = container[key]
        if IImage.providedBy(image):
                return image
        else:
            raise KeyError(key)
            

    # adaption of zope.interface.common.mapping.IReadMapping
    def get(self, key, default=None):
        # private resources
        container = self._getContainer()

        # preconditions
        if container is None:
            return default

        # essentials
        image = container.get(key, default)
        if IImage.providedBy(image):
                return image
        else:
            return default 

    def __contains__(self, key):
        return (key in self.keys())

    # adaption of zope.interface.common.mapping.IEnumerableMapping
    def keys(self):
        return [key for key, value in self.items()]

    def __iter__(self):
        return iter(self.items())

    def values(self):
        return [value for key, value in self.items()]

    def items(self):
        # private resources
        container = self._getContainer()
        images = []

        # preconditions
        if container is None:
            return images

        # essentials
        for item in container.items():
            if IImage.providedBy(item[1]):
                images.append(item)

        return images

    def __len__(self):
        return len(self.items())
        
            

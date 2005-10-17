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

$Id: views.py 7083 2004-10-21 15:56:05Z dhuber $
"""

from zope.event import notify
from zope.interface import implements
from zope.security.interfaces import Unauthorized

from zope.app import zapi
from zope.app.dublincore.interfaces import IZopeDublinCore
from zope.app.container.interfaces import IContainer
from zope.app.event.objectevent import ObjectModifiedEvent
from zope.app.publisher.browser import BrowserView

from kupusupport.interfaces import IImageReadContainer
from kupusupport.interfaces import IImageLibrary
from kupusupport.interfaces import IImageLibraryInfo
from kupusupport.interfaces import IKupuPolicy

try :
    from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
except :
    pass # only needed for tests

class KupuEditor(BrowserView):
    """Kupu editor view

    Preparation::

        >>> from zope.app.tests import placelesssetup, ztapi
        >>> from zope.publisher.browser import TestRequest

        >>> from kupusupport.interfaces import IKupuPolicy
        >>> from kupusupport.sample import IKupuSample
        >>> from kupusupport.sample.adapters import KupuSamplePolicy
        >>> from kupusupport.sample.app import KupuSample

        >>> placelesssetup.setUp()

    Register specific policy adapter::
    
        >>> ztapi.provideAdapter((IKupuSample,), IKupuPolicy, KupuSamplePolicy)
        >>> request = TestRequest()
        >>> content = KupuSample()
      
    We should be able to create a KupuEditor view on this
    content and update the content beneath:

        >>> editorview = KupuEditor(content, request)
        >>> kupu = '...<body>Updated value</body>...'
        >>> editorview.update(kupu)
        >>> editorview.display()
        u'Updated value'

    Make sure it redirected to kupueditor.html:
    
        >>> request.response.getStatus()
        302
        >>> request.response.getHeader('location')
        'kupueditor.html'

    There should be an ObjectModifiedEvent event logged:

        >>> from zope.app.event.tests.placelesssetup import getEvents
        >>> from zope.app.event.interfaces import IObjectModifiedEvent
        >>> [event] = getEvents(IObjectModifiedEvent)
        >>> event.object is content
        True

        >>> placelesssetup.tearDown()
    """

    implements(IKupuPolicy)

    def __init__(self, context, request):
        super(KupuEditor, self).__init__(context, request)
        #self.src = zapi.getView(None, 'absolute_url', request)
        #self.dst = zapi.getView(None, 'absolute_url', request)
        #self.use_css = False
        #self.reload_after_save = False
        #self.strict_output = False

    # pagetemplates provided by the ediorview itself
    try :
        _macros = ViewPageTemplateFile('kupumacros.pt')
    except :
        pass # only needed for test purposes. Examine later on XXX
        
    def __getitem__(self, key):
        return self._macros.macros[key]

    # implementation of kupusupport.IKupuPolicy
    def update(self, kupu=None):
        # lookup policy adapter to update changes
        if kupu:
            policy = IKupuPolicy(self.context)
            policy.update(kupu)
            notify(ObjectModifiedEvent(self.context))

        self.request.response.redirect("kupueditor.html")

    def display(self):
        # lookup policy adapter to display content which should be 
        # editable by kupu
        policy = IKupuPolicy(self.context)
        return policy.display()


class ImageLibraryInfo(BrowserView):
    """Image library info view

    Preparation::

        >>> from zope.interface import directlyProvides
        >>> from zope.publisher.browser import TestRequest
        >>> from zope.app.annotation.interfaces import IAttributeAnnotatable, IAnnotations
        >>> from zope.app.annotation.attribute import AttributeAnnotations
        >>> from zope.app.dublincore.annotatableadapter import ZDCAnnotatableAdapter
        >>> from zope.app.dublincore.interfaces import IWriteZopeDublinCore
        >>> from zope.app.tests import setup, ztapi
        >>> from zope.app.file.interfaces import IImage

        >>> from kupusupport.adapters import ImageReadContainer
        >>> from kupusupport.sample import IKupuSample
        >>> from kupusupport.sample.app import KupuSample

        >>> setup.placefulSetUp()
        
        >>> from zope.app.folder import rootFolder
        

    Register necessary adapters. Create root folder and request::
    
        >>> ztapi.provideAdapter((IKupuSample,), 
        ...     IImageReadContainer, ImageReadContainer)
        >>> ztapi.provideAdapter((IAttributeAnnotatable,), 
        ...     IAnnotations, AttributeAnnotations)
        >>> ztapi.provideAdapter((IAttributeAnnotatable,),
        ...     IWriteZopeDublinCore, ZDCAnnotatableAdapter)
        >>> root = rootFolder()
        >>> request = TestRequest()

    Prepare test content first. The marker interfaces IImageLibrary and 
    IAttributeAnnotatable has to be provided::

        >>> content = KupuSample()
        >>> directlyProvides(content, IImageLibrary, IAttributeAnnotatable)
        >>> IImageLibrary.providedBy(content)
        True

        >>> root['foo'] = content
        >>> IImageLibrary.providedBy(content)
        True
      
    We should be able to create a ImageLibraryInfo view::

        >>> view = ImageLibraryInfo(root['foo'], request)
        >>> view.libraryInfos()
        []
        >>> view.imageInfos()
        []

    We can add an image as containment. Afterward the method imageInfos should
    reflect this change::

        >>> from zope.app.file.image import Image
        >>> image = Image()
        >>> directlyProvides(image, IAttributeAnnotatable)
        >>> content['image'] = image

        >>> view.libraryInfos()
        []
        >>> [(info['title'], info['url']) for info in view.imageInfos()]
        [(u'image', 'http://127.0.0.1/foo/image')]

    The kupu sample might contain other image libraries. Such contained image libraries can be
    looked up by the method libraryInfos::

        >>> subcontent = KupuSample()
        >>> directlyProvides(subcontent, IImageLibrary, IAttributeAnnotatable)
        >>> root['foo']['bar'] = subcontent

        >>> [(info['title'], info['url']) for info in view.libraryInfos()]
        [(u'bar', 'http://127.0.0.1/foo/bar')]
        >>> [(info['title'], info['url']) for info in view.imageInfos()]
        [(u'image', 'http://127.0.0.1/foo/image')]

        >>> setup.placefulTearDown()
    """

    implements(IImageLibraryInfo)

    # private resources
    def _safe_getattr(self, obj, attr, default):
        """Attempts to read the attr, returning default if Unauthorized."""
        try:
            return getattr(obj, attr, default)
        except Unauthorized:
            return default

    # pagetemplates provided by the image library itself
    try :
        imagelibraries = ViewPageTemplateFile('imagelibraries.pt')
    except :
        pass

    # implementation of kupusupport.IImageLibraryInfo
    def libraryInfos(self):
        # resources
        container = IContainer(self.context, None)
        infos = []

        # preconditions
        if container is None:
            return infos
        
        # essentials        
        for key, value in container.items():
            if not IImageLibrary.providedBy(value):
                continue

            dc = IZopeDublinCore(value)
            info = {}
            info['name'] = key
            info['title'] = self._safe_getattr(dc, 'title', u'')
            if not info['title']:
                info['title'] = key
            info['description'] = self._safe_getattr(dc, 'description', u'')
            info['url'] = str(zapi.getView(value, 'absolute_url', self.request))
            infos.append(info)
       
        return infos

    def imageInfos(self):
        # resources
        imagecontainer = IImageReadContainer(self.context, None)
        infos = []

        # preconditions
        if imagecontainer is None:
            return infos

        # essentials        
        for key, value in imagecontainer.items():
            dc = IZopeDublinCore(value)
            info = {}
            info['name'] = key
            info['title'] = self._safe_getattr(dc, 'title', u'')
            if not info['title']:
                info['title'] = key
            info['description'] = self._safe_getattr(dc, 'description', '')
            info['width'], info['height'] = value.getImageSize()
            info['size'] = value.getSize()
            info['url'] = str(zapi.getView(value, 'absolute_url', self.request))
            infos.append(info)
       
        return infos

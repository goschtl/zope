from zope.size.interfaces import ISized
from zope.app.file.image import getImageInfo
from zope.size import byteDisplay
from interfaces.filetypes import IImageFile
from zope import component, interface
from zope.app.i18n import ZopeMessageFactory as _

class ImageFileSized(object):
    interface.implements(ISized)
    component.adapts(IImageFile)
    
    def __init__(self, image):
        self._image = image

    def sizeForSorting(self):
        '''See `ISized`'''
        return ('byte', self._image.getSize())

    def sizeForDisplay(self):
        '''See `ISized`'''
        t, w, h = getImageInfo(self._image.data.read(256))
        if w < 0:
            w = '?'
        if h < 0:
            h = '?'
        bytes = self._image.getSize()
        byte_size = byteDisplay(bytes)
        mapping = byte_size.mapping
        if mapping is None:
            mapping = {}
        mapping.update({'width': str(w), 'height': str(h)})
        #TODO the way this message id is defined, it won't be picked up by
        # i18nextract and never show up in message catalogs
        return _(byte_size + ' ${width}x${height}', mapping=mapping)

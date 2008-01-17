from zope.interface import implements
from zope import component
from z3c.image.image import VImage
from zope.app.file.interfaces import IFile
from zope.cachedescriptors.property import readproperty
from cStringIO import StringIO
from interfaces import IProcessableImage
from PIL import ImageFile, Image
from types import StringType
from zope.app.cache.ram import RAMCache
import os
import logging
try:
    ulimit = int(os.popen('ulimit -n').read().strip())
    maxEntries = ulimit - 100
except:
    ulimit = -1
    maxEntries = 100

# see http://mail.python.org/pipermail/image-sig/2003-May/002228.html
ImageFile.MAXBLOCK = 1024*1024*10
imgCache = RAMCache()
maxEntries = min(maxEntries, 400)
logging.debug('z3c.image.proc init imgCache maxEntries: %r, ulimit %r' % (
    maxEntries, ulimit))
imgCache.maxEntries = maxEntries

def invalidateCache(object, event):
    imgCache.invalidate(object)


class ProcessableImage(object):

    component.adapts(IFile)
    implements(IProcessableImage)

    def __init__(self, image):
        self.context = image
        self.format = ''
        contentType = image.contentType
        if contentType is not None:
            try:
                self.format = image.contentType.split('/')[1]
            except IndexError:
                pass
        self.cmds = []

    def getPILImg(self):
        data = self.context.data
        if type(data)!=StringType:
            data.seek(0)
            data = data.read()
        p = Image.open(StringIO(data))
        return p

    def _toImage(self, pimg, *args,**kw):
        """returns an Image object from the given PIL image"""
        if self.format == 'gif':
            # optimization seems to create corrupted gif files wiht
            # PIL, so we switch it off
            kw.pop('optimize')
        img = VImage(contentType=self.context.contentType,
                     size=pimg.size)
        try:
            pimg.save(img.data,self.format,*args,**kw)
        except IOError:
            # retry without optimization
            kw.pop('optimize')
            pimg.save(img.data,self.format,*args,**kw)
        img.data.seek(0)
        return img

    def rotate(self, degrees):
        self.cmds.append(('rotate',(degrees,),{}))

    def crop(self, croparea):
        croparea = map(int,croparea)
        self.cmds.append(('crop',(croparea,),{}))

    def resize(self, size):
        """See IPILImageResizeUtility"""
        size = map(int, size)
        self.cmds.append(('resize',(size, Image.ANTIALIAS),{}))

    def paste(self, img, box=None, mask=None):
        if box is not None:
            box = tuple(map(int, box))
        self.cmds.append(('paste',(img, box, mask), {}))

    def reset(self):
        self.cmds=[]

    def process(self,quality=90,optimize=1):
        """processes the command queue and returns the image"""
        if not self.cmds:
            return self.context
        key = {'cmds':str(self.cmds)}
        img = imgCache.query(self.context , key)
        if img is not None and not img.data.closed:
            img.data.seek(0)
            return img
        pimg = self.getPILImg()

        for name,args,kwords in self.cmds:
            func = getattr(pimg,name)
            oldImg = pimg
            pimg = func(*args,**kwords)
            if pimg is None:
                pimg = oldImg

        img = self._toImage(pimg, quality=quality, optimize=optimize)
        imgCache.set(img, self.context, key=key)
        return img

from zope.interface import implements
from zope import component
from z3c.image.image import VImage
from zope.app.file.interfaces import IFile
from zope.cachedescriptors.property import readproperty
from PIL import Image as PILImage
from cStringIO import StringIO
from interfaces import IProcessableImage
from PIL import ImageFile, Image
from types import StringType
from zope.app.cache.ram import RAMCache
import os
try:
    maxEntries = int(os.popen('ulimit -n').read().strip()) - 100
except:
    maxEntries = 100
    
# see http://mail.python.org/pipermail/image-sig/2003-May/002228.html
ImageFile.MAXBLOCK = 1024*1024*10
imgCache = RAMCache()
imgCache.maxEntries = maxEntries

class ProcessableImage(object):

    component.adapts(IFile)
    implements(IProcessableImage)

    def __init__(self,image):
        self.context = image
        self.format = image.contentType.split('/')[1]
        self.cmds = []

    def getPILImg(self):
        data = self.context.data
        # only make it a buffer if we need to, so we can handle
        # efficient files, like from z3c.extfile
        p = ImageFile.Parser()
        if type(data)==StringType:
            p.feed(data)
        else:
            data.seek(0)
            while 1:
                s = data.read(1024)
                if not s:
                    try:
                        data.close()
                    except:
                        pass
                    break
                p.feed(s)
        return p.close()
        
    def _toImage(self, pimg, *args,**kw):
        """returns an Image object from the given PIL image"""
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
        size = map(int,size)
        self.cmds.append(('resize',(size, Image.ANTIALIAS),{}))

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
            pimg = func(*args,**kwords)

        img = self._toImage(pimg, quality=quality, optimize=optimize)
        imgCache.set(img, self.context, key=key)
        return img

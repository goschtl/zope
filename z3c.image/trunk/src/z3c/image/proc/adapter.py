from zope.interface import implements
from zope import component
from zope.app.file import Image
from zope.app.file.interfaces import IFile
from zope.cachedescriptors.property import readproperty
from PIL import Image as PILImage
from cStringIO import StringIO
from interfaces import IProcessableImage
from PIL import ImageFile
from types import StringType

# see http://mail.python.org/pipermail/image-sig/2003-May/002228.html
ImageFile.MAXBLOCK = 1024*1024

class ProcessableImage(object):

    component.adapts(IFile)
    implements(IProcessableImage)

    def __init__(self,image):
        self.context = image
        self.format = image.contentType.split('/')[1]
        self.cmds = []

    @readproperty
    def pimg(self):
        data = self.context.data
        # only make it a buffer if we need to, so we can handle
        # efficient files, like from z3c.extfile
        if type(data)==StringType:
            data = StringIO(data)
        return PILImage.open(data)
        
    def _toImage(self,*args,**kw):
        """returns an Image object from the given PIL image"""
        data = StringIO()
        try:
            self.pimg.save(data,self.format,*args,**kw)
        except IOError:
            # retry without optimization
            kw.pop('optimize')
            self.pimg.save(data,self.format,*args,**kw)
        return Image(data.getvalue())

    def rotate(self, degrees):
        self.cmds.append(('rotate',[degrees],{}))

    def crop(self, croparea):
        croparea = map(int,croparea)
        self.cmds.append(('crop',[croparea],{}))
    
    def resize(self, size):
        """See IPILImageResizeUtility"""
        size = map(int,size)
        self.cmds.append(('resize',[size],{}))

    def reset(self):
        self.cmds=[]
        
    def process(self,quality=90,optimize=1):
        """processes the command queue and returns the image"""
        if not self.cmds:
            return self.context
        for name,args,kwords in self.cmds:
            func = getattr(self.pimg,name)
            self.pimg = func(*args,**kwords)
        return self._toImage(quality=quality,optimize=optimize)

        
        

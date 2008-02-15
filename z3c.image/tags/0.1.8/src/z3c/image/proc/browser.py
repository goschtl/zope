import time
import PIL
from datetime import datetime
from cStringIO import StringIO
from types import StringType

import zope.datetime

from zope.security.proxy import isinstance, removeSecurityProxy
from zope.publisher.browser import BrowserView
from zope.dublincore.interfaces import IZopeDublinCore

from zope.app.file.image import getImageInfo

from interfaces import IProcessableImage


def getMaxSize(image_size, desired_size):
    """returns the maximum size of image_size to fit into the
    rectangualar defined by desired_size

    >>> getMaxSize((100,200),(100,100))
    (50, 100)

    >>> getMaxSize((100,300),(100,100))
    (33, 100)

    >>> getMaxSize((300,100),(100,100))
    (100, 33)

    >>> getMaxSize((300,100),(400,200))
    (400, 133)


    """
    x_ratio = float(desired_size[0])/image_size[0]
    y_ratio = float(desired_size[1])/image_size[1]
    if x_ratio < y_ratio:
        new_size = (round(x_ratio*image_size[0]),
                    round(x_ratio*image_size[1]))
    else:
        new_size = (round(y_ratio*image_size[0]),
                    round(y_ratio*image_size[1]))
    return tuple(map(int, new_size))


class ImageProcessorView(BrowserView):

    """image processor"""

    def __init__(self,context,request):
        super(ImageProcessorView,self).__init__(context,request)
        self.degrees =int(self.request.form.get('remote.adjust.rotate',0))
        self.width = int(self.request.form.get('remote.size.w',0))
        self.height = int(self.request.form.get('remote.size.h',0))

        self.cropX = self.request.form.get('local.crop.x',None)
        self.cropW = self.request.form.get('local.crop.w',None)
        self.cropY = self.request.form.get('local.crop.y',None)
        self.cropH = self.request.form.get('local.crop.h',None)

        self.afterSizeW = int(self.request.form.get('after.size.w',0))
        self.afterSizeH = int(self.request.form.get('after.size.h',0))

        self.size = (self.width,self.height)
        self._calcAfterSize()

    @property
    def data(self):
        context = removeSecurityProxy(self.context)
        data = context.data
        if not isinstance(data, str):
            pos = data.tell()
            data.seek(0)
            res = data.read(1024*1024)
            data.seek(pos)
            data = res
        else:
            data = context.data
        return data

    def _resultingRatio(self):
        if (    self.cropW is not None
            and self.cropH is not None
            and self.cropW != 0
            and self.cropH != 0
           ):
            ratio = float(self.cropW) / float(self.cropH)
        else:
            t,w,h = getImageInfo(self.data)
            ratio = float(w) / float(h)
        return ratio

    def _calcAfterSize(self):
        if (self.afterSizeW == 0 or self.afterSizeH == 0) and \
           self.afterSizeW != self.afterSizeH:
            ratio = self._resultingRatio()
            if self.afterSizeH == 0:
                self.afterSizeH = int(round(self.afterSizeW / ratio))
            if self.afterSizeW == 0:
                self.afterSizeW = int(round(self.afterSizeH * ratio))
        self.afterSize = (self.afterSizeW,self.afterSizeH)

    def _process(self):
        pimg = IProcessableImage(self.context)
        self._pushCommands(pimg)
        return pimg.process()

    def _pushCommands(self, pimg):
        if self.degrees > 0:
            pimg.rotate(self.degrees)
        if self.width and self.height:
            pimg.resize(self.size)
        if self.cropX is not None and self.cropY is not None \
           and self.cropW is not None and self.cropH is not None:
            self.croparea = (int(self.cropX),
                             int(self.cropY),
                             int(self.cropX) + int(self.cropW),
                             int(self.cropY) + int(self.cropH))
            pimg.crop(self.croparea)
        if self.afterSizeW is not 0 and self.afterSizeH is not 0:
            if self.cropW and self.cropH:
                currentSize = (int(self.cropW), int(self.cropH))
            elif self.width and self.height:
                currentSize = (self.width, self.height)
            else:
                t,w,h = getImageInfo(self.data)
                currentSize = (w,h)
            size=getMaxSize(currentSize, self.afterSize)
            pimg.resize(size)
        return pimg.process()

    def processed(self):
        processed = self._process()
        if self.request is not None:
            self.request.response.setHeader('Content-Type',
                                            processed.contentType)
            self.request.response.setHeader('Content-Length',
                                            processed.getSize())
        return processed.data

    def __call__(self):
        try:
            modified = IZopeDublinCore(self.context).modified
        except TypeError:
            modified=None
        if modified is None or not isinstance(modified,datetime):
            return self.processed()
        header= self.request.getHeader('If-Modified-Since', None)
        lmt = long(time.mktime(modified.timetuple()))
        if header is not None:
            header = header.split(';')[0]
            try:    mod_since=long(zope.datetime.time(header))
            except: mod_since=None
            if mod_since is not None:
                if lmt <= mod_since:
                    self.request.response.setStatus(304)
                    return ''
        self.request.response.setHeader('Last-Modified',
                                        zope.datetime.rfc1123_date(lmt))
        return self.processed()


class ResizedImageView(ImageProcessorView):

    def __init__(self,context,request):
        super(ResizedImageView,self).__init__(context,request)
        data = context.data
        if not isinstance(data, str):
            pos = data.tell()
            data.seek(0)
            res = data.read(1024*1024)
            data.seek(pos)
            data = res
        else:
            data = self.context.data
        t,w,h = getImageInfo(data)
        self.size = (w,h)
        self.width = self.request.form.get('w',self.size[0])
        self.height = self.request.form.get('h',self.size[1])

    def _pushCommands(self, pimg):
        new_size = getMaxSize(self.size, (self.width, self.height))
        if new_size != self.size:
            pimg.resize(new_size)


class PasteImageView(ResizedImageView):
    """Paste an image into the image.

    The subclass must provide the image to be pasted.
    """

    img = None

    def __init__(self,context,request):
        super(PasteImageView, self).__init__(context, request)
        self.x = self.request.form.get('x', 0)
        self.y = self.request.form.get('y', 0)
        self.imgId = self.request.form.get('img', 0)

    def _pushCommands(self, pimg):
        super(PasteImageView, self)._pushCommands(pimg)
        img = self.img
        if img is not None:
            if type(img)!=StringType:
                img.seek(0)
                img = img.read()
            img = PIL.Image.open(StringIO(img))
            pimg.paste(img, (self.x, self.y), img)


from z3c.blobfile.browser.file import FileView
from zope.app.file.browser.image import ImageData

class ImageData(FileView, ImageData):
    '''Image view with zope.app.file's show method overriden by z3c.blobfile's one'''

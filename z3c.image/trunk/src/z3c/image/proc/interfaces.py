from zope.interface import Interface

class IProcessableImage(Interface):

    def process():
        """returns the processed image"""

    def rotate(degrees):
        """rotates the image by degrees"""

    def resize(size):
        """resizes the image to (w,h)"""

    def crop(croparea):
        """ crops the image """

    def paste(pos, img, mask):
        """ paste an image at pos with mask"""


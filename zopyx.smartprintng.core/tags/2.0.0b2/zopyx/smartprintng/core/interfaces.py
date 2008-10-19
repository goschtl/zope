##########################################################################
# zopyx.smartprintng.core - High-quality export of Zope content to
# PDF, RTF, ODT, WML and DOCX
#
# (C) 2007, 2008, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################


from zope.interface import Interface


class IHTMLTransformation(Interface):
    """ Interface for HTML transformation
        (based on the BeautifulSoup module)
    """

    def __init__(html=None, soup=None):
        """ Constructor that accepts either unicode
            HTML string or a BeautifulSoup instance.
        """

    def transform():
        """ execute the transformation """


class IImageFetcher(Interface):
    """ Retrieve image data either from a local site
        or a remote site.
    """

    def fetch(src):
        """ Return the image data for the given src. This
            can either be a relative URL or an absolute URL. Images
            with a absolute URL should be downloaded using HTTP. Images
            represented using a relative URL should be access through
            traversal based on the 'context' object defined through
            the constructor.
        """
              

class IHTMLExtractor(Interface):
    """ Extract a HTML snippet from the current object """

    def getHTML():
        """ Returns a HTML snippet to be converted for the current
            object. The method *must not* returne a full HTML page.
            An optional context object will be passed if the interface
            is implemented by an utility.
        """



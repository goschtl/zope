##########################################################################
# zopyx.smartprintng.core - High-quality export of Zope content to
# PDF, RTF, ODT, WML and DOCX
#
# (C) 2007, 2008, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import urllib2
import urlparse

from zope.interface import implements
from interfaces import IImageFetcher

class ExternalImageFetcher(object):
    """ Adapter for fetching images from an external URL """

    implements(IImageFetcher)

    def __init__(self, context):
        self.context = context

    def fetch(self, src):

        img_tp = urlparse.urlparse(src)
        if not img_tp[0] in ('http', 'https', 'ftp'):
            raise ValueError('Unable to handle image reference %s' % src)

        try:
            return urllib2.urlopen(src).read()
        except Exception, e:
            raise ValueError('Image could not be downloaded from %s (%s)' % (src, e))

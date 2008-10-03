##########################################################################
# zopyx.convert - XSL-FO related functionalities
#
# (C) 2007, 2008, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

from zope.interface import Interface

class IHTMLConverter(Interface):

    def convertHtml(html_filename, output_filename=None):
        """ Converts the HTML stored in file references as
            ``html_filename`` to some output format. The conversion
            result is also stored on the filesystem. The filename 
            of the converted is file is returned.
        """
            

class IFOConverter(Interface):

    def convert(fo_filename):
        """ Convert a XSL-FO file (stored on the filesystem) to some output format.
            Returns the filename of the output file. 
        """


class IHTML2FOConverter(Interface):
        
    def convert(html_filename):
        """ Convert a HTML file (stored on the filesystem to XSL-FO.    
        """


class IXSLFOConverter(Interface):
    """ A converter that converts HTML to some output format using
        XSL-FO.
    """

    def __init__(filename, encoding='utf-8', cleanup=False, verbose=False):
        """ Initialize a converter with the 'filename' of a HTML file """

    def convert(format, output_filename=None):
        """ Convert HTML to output 'format' """

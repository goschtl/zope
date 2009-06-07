##########################################################################
# zopyx.convert - XSL-FO related functionalities
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os

from zope.interface import implements

from interfaces import IXSLFOConverter
from config import supported_formats
from html2fo import HTML2FOConverter
from fo2xfc import (xfc_available, RTFConverter, ODTConverter, 
                    WMLConverter, DOCXConverter)
from fo2pdf import xinc_available, PDFConverter
from fo2fop import fop_available, FOPPDFConverter
from princexml import princexml_available, PrinceXMLConverter


class Converter(object):
    """High-level OO interface to XSL-FO conversions """

    implements(IXSLFOConverter)

    def __init__(self, filename, encoding='utf-8', cleanup=False, verbose=False):
        self.filename = filename
        self.encoding = encoding
        self.fo_filename = None        
        self.cleanup = cleanup
        self.verbose = verbose

    def convert(self, format, output_filename=None, **options):
        """ 'options' is passwd down html2fo() """

        if format == 'fo':
            if self.fo_filename is None:
                self.fo_filename = HTML2FOConverter().convert(self.filename, self.encoding, **options)
            return self.fo_filename

        if not format in supported_formats:
            raise ValueError('Unsupported format: %s' % format)

        if self.fo_filename is None and format not in ('pdf3',):
            self.fo_filename = HTML2FOConverter().convert(self.filename, self.encoding, **options)

        if format == 'pdf':
            if not xinc_available:
                raise RuntimeError("The external XINC converter isn't available")
            output_filename = PDFConverter().convert(self.fo_filename, output_filename=output_filename)

        elif format == 'pdf2':
            if not fop_available:
                raise RuntimeError("The external FOP converter isn't available")
            output_filename = FOPPDFConverter().convert(self.fo_filename, output_filename=output_filename)

        elif format == 'pdf3':
            if not princexml_available:
                raise RuntimeError("The external PrinceXML isn't available")
            output_filename = PrinceXMLConverter().convert(self.filename, output_filename=output_filename)

        else:
            if not xfc_available:
                raise RuntimeError("The external XFC converter isn't available")

            map = {'odt' : ODTConverter,
                   'rtf' : RTFConverter,
                   'docx' : DOCXConverter,
                   'wml' : WMLConverter }
            output_filename = map[format]().convert(self.fo_filename, output_filename=output_filename)

        return output_filename

    def __call__(self, *args, **kw):
        return self.convert(*args, **kw)

    def __del__(self):
        """ House-keeping """

        if self.cleanup:
            if self.fo_filename:
                os.unlink(self.fo_filename)


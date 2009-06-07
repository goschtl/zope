##########################################################################
# zopyx.convert - XSL-FO related functionalities
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

from interfaces import IFOConverter, IHTML2FOConverter, IXSLFOConverter

from convert import Converter
from html2fo import HTML2FOConverter
from fo2pdf import PDFConverter, xinc_available
from fo2fop import FOPPDFConverter, fop_available
from fo2xfc import DOCXConverter, RTFConverter, ODTConverter, WMLConverter, xfc_available
from princexml import PrinceXMLConverter, princexml_available

def availableFormats():

    formats = []
    if xinc_available:
        formats.append('pdf')
    if fop_available:
        formats.append('pdf2')
    if princexml_available:
        formats.append('pdf3')
    if xfc_available:
        formats.extend(['rtf', 'docx', 'odt', 'wml'])

    return formats

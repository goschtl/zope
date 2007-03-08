===================
The Template Parser
===================

This document demonstrates the parsing capabilities of the PML-to-PDF template
parser.

  >>> from z3c.pdftemplate.pml2pdf.Parser import TemplateParser

To make life easier, we create a simple helper function that converts an XML
string to a DOM tree and creates the template object using the parser:

  >>> import xml.dom.minidom
  >>> def getTemplate(xml_string):
  ...     dom = xml.dom.minidom.parseString(xml_string)
  ...     return TemplateParser(dom, 'utf-8')()

``template`` Element
--------------------

The most outer XML element for the template file is the ``template`` element.

  >>> template = getTemplate('''<?xml version="1.0" encoding="utf-8"?>
  ...     <template
  ...         filename="contents.pdf"
  ...         pagesize="A4"
  ...         landscape="0"
  ...         showboundary="0"
  ...         leftmargin="1cm"
  ...         rightmargin="1cm"
  ...         topmargin="1cm"
  ...         bottommargin="1cm"
  ...         allowsplitting="1">
  ...     </template>''')

  >>> template.filename
  'contents.pdf'
  >>> template.showBoundary
  0
  >>> int(template.leftMargin)
  28
  >>> int(template.rightMargin)
  28
  >>> int(template.topMargin)
  28
  >>> int(template.bottomMargin)
  28
  >>> template.allowSplitting
  1


``stylesheet`` Element
----------------------

This is just a grouping element and has no functionality in itself. The
following elements can be contained in this element.


``paragraphstyle`` Element
--------------------------

  >>> template = getTemplate('''<?xml version="1.0" encoding="utf-8"?>
  ...     <template><stylesheet>
  ...       <paragraphstyle
  ...           name="BodyText"
  ...           fontName="Helvetica"
  ...           fontSize="10"
  ...           align="LEFT"
  ...           firstLineIndent="0cm"
  ...           leftIndent="0.5cm"
  ...           rightIndent="0cm"
  ...           spaceBefore="0"
  ...           spaceAfter="0"
  ...           leading="0.5cm"
  ...           bulletFontName="Helvetica"
  ...           bulletIndent="0cm"
  ...           bulletFontSize="10" />
  ...     </stylesheet></template>''')

  >>> para = template.getStyleSheet()['BodyText']
  >>> para.fontName
  'Helvetica'
  >>> para.bulletFontName
  'Helvetica'
  >>> para.parent is None
  True
  >>> para.firstLineIndent
  0.0
  >>> int(para.leftIndent)
  14
  >>> para.rightIndent
  0.0
  >>> para.backColor is None
  True
  >>> para.alignment
  0
  >>> para.name
  'BodyText'
  >>> int(para.leading)
  14
  >>> para.bulletIndent
  0.0
  >>> para.bulletFontSize
  10
  >>> para.fontSize
  10
  >>> para.textColor
  Color(0,0,0)
  >>> para.spaceBefore
  0.0
  >>> para.spaceAfter
  0.0


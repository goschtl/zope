=======================================
A Python interface to XSL-FO libraries. 
=======================================

The zopyx.convert package helps you to convert HTML to PDF, RTF, ODT, DOCX and
WML using XSL-FO technology.


Requirements
============

- Java 1.5.0 or higher (FOP 0.94 requires Java 1.6 or higher)

- `csstoxslfo`__ (included)

__ http://www.re.be/css2xslfo

- `XFC-4.0`__ (XMLMind) for ODT, RTF, DOCX and WML support (if needed)

__ http://www.xmlmind.com/foconverter

- `XINC 2.0`__ (Lunasil) for PDF support (commercial)

__ http://www.lunasil.com/products.html

- or `FOP 0.94`__ (Apache project) for PDF support (free)

__ http://xmlgraphics.apache.org/fop/download.html#dist-type                                            

- or `PrinceXML`__ for PDF support (commercial)

__ http://www.princexml.com/

- `BeautifulSoup`__  (will be installed automatically through easy_install. See Installation.)

__ http://www.crummy.com/software/BeautifulSoup/
   
- `ElementTree`__ (will be installed automatically through easy_install. See Installation.)

__ http://effbot.org/zone/element-index.html

Installation
============

- install **zopyx.convert** either using ``easy_install`` or by downloading the sources from the Python Cheeseshop. 
  This will install automatically the Beautifulsoup and Elementree modules if necessary.
- the environment variable *$XFC_DIR* must be set and point to the root of your XFC installation directory
- the environment variable *$XINC_HOME* must be set and to point to the root of your XINC installation directory
- the environment variable *$FOP_HOME* must be set and point to the root of your FOP installation directory

Supported platforms
===================

Windows, Unix


Subversion repository
=====================

- http://svn-public.zopyx.com/viewvc/python-projects/zopyx.convert/trunk/


Usage
=====

Some examples from the Python command-line::

  from zopyx.convert import Converter
  C = Converter('/path/to/some/file.html')
  pdf_filename = C('pdf')         # using XINC
  pdf2_filename = C('pdf2')       # using FOP
  rtf_filename = C('rtf')
  pdt_filename = C('odt')
  wml_filename = C('wml')
  docx_filename = C('docx')

A very simple command-line converter is also available::

  xslfo-convert --format rtf --output foo.rtf sample.html


`xslfo-convert` has a --test option that will convert some
sample HTML. If everything is ok then you should see something like that::

  >xslfo-convert --test
  Entering testmode
  pdf: /tmp/tmpuOb37m.html -> /tmp/tmpuOb37m.pdf
  rtf: /tmp/tmpuOb37m.html -> /tmp/tmpuOb37m.rtf
  docx: /tmp/tmpuOb37m.html -> /tmp/tmpuOb37m.docx
  odt: /tmp/tmpuOb37m.html -> /tmp/tmpuOb37m.odt
  wml: /tmp/tmpuOb37m.html -> /tmp/tmpuOb37m.wml
  pdf: /tmp/tmpZ6PGo9.html -> /tmp/tmpZ6PGo9.pdf
  rtf: /tmp/tmpZ6PGo9.html -> /tmp/tmpZ6PGo9.rtf
  docx: /tmp/tmpZ6PGo9.html -> /tmp/tmpZ6PGo9.docx
  odt: /tmp/tmpZ6PGo9.html -> /tmp/tmpZ6PGo9.odt
  wml: /tmp/tmpZ6PGo9.html -> /tmp/tmpZ6PGo9.wml


How zopyx.convert works internally
==================================

- The source HTML file is converted to XHTML using mxTidy
- the XHTML file is converted to FO using the great "csstoxslfo" converter
  written by Werner Donne.
- the FO file is passed either to the external XINC or XFC converter to 
  generated the desired output format
- all converters are based on Java technology make the conversion solution
  highly portable across operating system (including Windows)

Known issues
============

If you are using zopyx.convert together with FOP: use the latest FOP 0.94 only.
Don't use any packaged FOP version like the one from MacPorts which is known to be
broken.    

Author
======

**zopyx.convert** was written by Andreas Jung for ZOPYX Ltd. & Co. KG, Tuebingen, Germany.


License
=======

**zopyx.convert** is published under the Lesser GNU Public License V 2.1 (LGPL 2.1).
See LICENSE.txt.


Contact
=======

| ZOPYX Ltd. & Co. KG
| c/o Andreas Jung, 
| Charlottenstr. 37/1
| D-72070 Tuebingen, Germany
| E-mail: info at zopyx dot com
| Web: http://www.zopyx.com

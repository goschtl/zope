=====================================
Using ReportLab to generate PDF Views
=====================================

This package,

  >>> import z3c.pdftemplate

provides the functionality of creating browser views that generate PDFs
instead of HTML using reportlab's PDF writer technology. There are several
ways to use the features in this package, which are demonstrated in the text
below.

But first we have to load the directives' meta configuration:

  >>> from zope.app import zapi
  >>> from zope.publisher.browser import TestRequest
  >>> from zope.configuration import xmlconfig
  >>> context = xmlconfig.file('meta.zcml', package=z3c.pdftemplate)


PML to PDF Views
----------------

PML, an XML-dialect developed by Ulrich Eck, is much like HTML in that it lets
you define the structure of a PDF document. The PML is dynamically generated
using page templates and then used to generate a PDF file.

Let's say we want to create a PDF that shows the contents of a folder. The
first step is to create a document template that contains the structure of the
PDF. The following folder contents document template is available in
``folder_contents.pt``::

  <?xml version="1.0" encoding="iso-8859-15"?>
  <document
      xmlns:tal="http://xml.zope.org/namespaces/tal"
      xmlns:metal="http://xml.zope.org/namespaces/metal"
      filename="contents.pdf">
  <content>

  <para style="FolderName">
    Folder Name:
    <tal:block
       condition="context/zope:name"
       replace="context/zope:name|default" />
    <tal:block condition="not:context/zope:name">&lt;no name&gt;</tal:block>
  </para>

  <spacer height="30" />

  <table splitbyrow="1" repeatrows="0" repeatcols="0" style="ContentTable">
    <tr>
      <td>Name</td>
      <td>Title</td>
      <td>Size</td>
      <td>Created</td>
      <td>Modified</td>
    </tr>
    <tr tal:repeat="item view/listContentInfo">
      <td tal:content="item/id">me.png</td>
      <td tal:content="item/title|default">&lt;no title&gt;</td>
      <td tal:content="item/size/sizeForDisplay|nothing">34.5 kB</td>
      <td tal:content="item/created|default"></td>
      <td tal:content="item/modified|default"></td>
    </tr>
  </table>

  <action name="frameEnd" />

  </content>
  </document>

Pretty easy isn't it? Fortunately, we can simply reuse the ``Contents`` view
class for the HTML contents view. Now that we have defined the document, we
have to create a PDF template, so that the table will look nice. The following
template code can be found in ``folder_template.pt``::

  <?xml version="1.0" encoding="utf-8"?>
  <template
      filename="contents.pdf"
      pagesize="A4"
      landscape="0"
      showboundary="0"
      leftmargin="1cm"
      rightmargin="1cm"
      topmargin="1cm"
      bottommargin="1cm"
      allowsplitting="1">

    <stylesheet>

     <paragraphstyle
         name="Base"
         fontName="Helvetica"
         fontSize="10"
         align="LEFT"
         firstLineIndent="0cm"
         leftIndent="0.5cm"
         rightIndent="0cm"
         spaceBefore="0"
         spaceAfter="0"
         leading="0.5cm"
         bulletFontName="Helvetica"
         bulletIndent="0cm"
         bulletFontSize="10" />

     <paragraphstyle
         name="FolderName"
         parent="Base"
         leftIndent="0cm"
         fontName="Helvetica-Bold"
         fontSize="16"
         leading="0.5cm"
         spaceBefore="4"
         spaceAfter="4" />

     <tablestyle name="ContentTable">
       <stylecmd expr="('LEFTPADDING', (0,0), (-1,-1), 5)"/>
       <stylecmd expr="('RIGHTPADDING', (0,0), (-1,-1), 5)"/>
       <stylecmd expr="('TOPPADDING', (0,0), (-1,-1), 3)"/>
       <stylecmd expr="('BOTTOMPADDING', (0,0), (-1,-1), 7)"/>
       <stylecmd expr="('ALIGN', (0,0), (-1,-1), 'LEFT')"/>
       <stylecmd expr="('GRID', (0,0), (-1,-1), 0.5, colors.black)"/>
       <stylecmd expr="('BOX', (0,0), (-1,-1), 1, colors.black)"/>
       <stylecmd expr="('FONT', (1,1), (-1,-1), 'Helvetica', 10)"/>
       <stylecmd expr="('FONT', (0,0), (-1,0), 'Helvetica-Bold', 10)"/>
       <stylecmd expr="('FONT', (0,1), (0,-1), 'Courier', 10)"/>
     </tablestyle>

    </stylesheet>


    <pagetemplate id="Page" >
      <static>
        <infostring
            align="left"
            x="5cm"
            y="28cm"
            size="10"
  	  font="Helvetica"
            color="(0, 0, 0)">
          The development of the PDF Template Code was sposored by Projekt01.
        </infostring>
      </static>

      <frame
          id="content"
     	nextid="content"
      	x="2cm"
          y="1.5cm"
  	width="17cm"
  	height="25.5cm"
  	leftpadding="0.1cm"
  	rightpadding="0.1cm"
  	toppadding="0.5cm"
  	bottompadding="0.5cm"
  	showBoundary="0" />
    </pagetemplate>

  </template>

Now that we have the template and the document, we can simply register the
view:

  >>> context = xmlconfig.string("""
  ...     <configure xmlns:browser="http://namespaces.zope.org/browser">
  ...       <browser:pml2pdf
  ...           name="sample_pml.pdf"
  ...           for="zope.app.folder.interfaces.IFolder"
  ...           template="sample/pml_template.pt"
  ...           document="sample/pml_contents.pt"
  ...           class="zope.app.container.browser.contents.Contents"
  ...           permission="zope.Public"
  ...           />
  ...     </configure>
  ...     """, context)

Once we have created a folder instance:

  >>> from zope.app.folder.folder import Folder
  >>> folder = Folder()
  >>> folder.__name__ = 'my folder'
  >>> folder['subFolder'] = Folder()

we can can look up the view

  >>> class Principal:
  ...   id = 'bob'

  >>> request = TestRequest()
  >>> request.setPrincipal(Principal())

  >>> contents = zapi.getMultiAdapter((folder, request),
  ...                                 name="sample_pml.pdf")

and create the PDF:

  #>>> contents() #doctest: +ELLIPSIS
  #'%PDF-1.3...'

Again, you cannot just register any template for the document. The styles that
are used in the document *must* be declared in the PDF template. In the
following case we are not specifying any template, so that the generic
template is used, which does not have the right styles defined:

  >>> context = xmlconfig.string("""
  ...     <configure xmlns:browser="http://namespaces.zope.org/browser">
  ...       <browser:pml2pdf
  ...           name="contents2.pdf"
  ...           for="zope.app.folder.interfaces.IFolder"
  ...           document="sample/pml_contents.pt"
  ...           class="zope.app.container.browser.contents.Contents"
  ...           permission="zope.Public"
  ...           />
  ...     </configure>
  ...     """, context)

  >>> contents = zapi.getMultiAdapter((folder, request),
  ...                                 name="contents2.pdf")
  >>> contents()
  Traceback (most recent call last):
  ...
      stylesheet[self.style],
  KeyError: 'FolderName'


Generic PDF Views
-----------------

Sometimes, however, you do not want to use PML to structure your content, but
use the reportlab API directly. But you still want to use the template
mechanism. For these cases there is a very simple directive that requires you
to implement a view class yourself. Let's use the simplest case possible and
create a PDF that returns an empty page.

The first step is to create the view class:

  >>> from StringIO import StringIO
  >>> class NullPage(object):
  ...
  ...     def __call__(self):
  ...         buffer = StringIO()
  ...         template = self.getPDFTemplate()
  ...         template.build([], buffer)
  ...
  ...         self.request.response.setHeader('content-type', 'application/pdf')
  ...         return buffer.getvalue()

We have to add the class to a loadable module:

  >>> z3c.pdftemplate.tests.NullPage = NullPage

Next we register the view:

  >>> context = xmlconfig.string("""
  ...     <configure xmlns:browser="http://namespaces.zope.org/browser">
  ...       <browser:pdf
  ...           name="null.pdf"
  ...           for="*"
  ...           class="z3c.pdftemplate.tests.NullPage"
  ...           permission="zope.Public"
  ...           />
  ...     </configure>
  ...     """, context)

  >>> contents = zapi.getMultiAdapter((None, request), name="null.pdf")
  >>> print contents() #doctest: +ELLIPSIS
  %PDF-1.3...

Doing some cleanup:

  >>> del z3c.pdftemplate.tests.NullPage


=====================================================
Using TinyRML2PDF and ReportLab to generate PDF Views
=====================================================

See ../INSTALL.txt and DEPENDENCIES.cfg, this lib depends on some 3rd party
libraries.


Purpose: PDF-Generration with the help of TinyRML (an open source implementation
of RML) and Reportlab.

We did some customizing in the RML-Language, so its possible to produce Chart
directly.


This package provides the functionality of creating browser views that
generate PDFs instead of HTML using reportlab's PDF writer technology.

But first we have to load the directives' meta configuration:

  >>> from zope.configuration import xmlconfig
  >>> context = xmlconfig.file('meta.zcml', package=z3c.pdftemplate)


RML, an XML-dialect developed by Reportlab.org, is much like HTML in that it
lets you define the structure of a PDF document. The RML is dynamically
generated using page templates and then used to generate a PDF file.


Let's say we want to create a PDF that shows the contents of a folder. The
first step is to create a rml-document that contains the structure of the
PDF. The following folder contents document template is available in
``rml_contents.pt``

::

<?xml version="1.0" encoding="iso-8859-1" standalone="no" ?>
<!DOCTYPE document SYSTEM "rml_1_0.dtd">
<document
    xmlns:tal="http://xml.zope.org/namespaces/tal"
    xmlns:metal="http://xml.zope.org/namespaces/metal"
    filename="contents.pdf">
<content>

<para style="FolderName">
  Folder Name:
  <tal:block
     condition="context/__name__"
     replace="context/__name__|default" />
  <tal:block condition="not:context/__name__">&lt;no name&gt;</tal:block>
</para>

<spacer height="30" />

<table splitbyrow="1" repeatrows="0" repeatcols="0" style="ContentTable">
  <tr>
    <td>Name</td>
    <td>Title</td>
    <td>Size</td>
    <td>Created</td>
    <td>Modified</td>
  </tr>
  <tr tal:repeat="item view/listContentInfo">
    <td tal:content="item/id">me.png</td>
    <td tal:content="item/title|default">&lt;no title&gt;</td>
    <td tal:content="item/size/sizeForDisplay|nothing">34.5 kB</td>
    <td tal:content="item/created|default"></td>
    <td tal:content="item/modified|default"></td>
  </tr>
</table>

<action name="frameEnd" />

</content>
</document>

Pretty easy isn't it? Fortunately, we can simply reuse the ``Contents`` view
class for the HTML contents view.

Now that we have the template and the document, we can simply register the
view:

  >>> context = xmlconfig.string("""
  ...     <configure xmlns:browser="http://namespaces.zope.org/browser">
  ...       <browser:rml2pdf
  ...           name="rmlsample.pdf"
  ...           for="zope.app.folder.interfaces.IFolder"
  ...           document="sample/rml_contents.pt"
  ...           class="zope.app.container.browser.contents.Contents"
  ...           permission="zope.Public"
  ...           />
  ...     </configure>
  ...     """, context)

Once we have created a folder instance:

  >>> from zope.app.folder.folder import Folder
  >>> folder = Folder()
  >>> folder.__name__ = 'my folder'
  >>> folder['subFolder'] = Folder()

we can can look up the view

  >>> class Principal:
  ...   id = 'bob'

  >>> request = TestRequest()
  >>> request.setPrincipal(Principal())

  >>> contents = zapi.getMultiAdapter((folder, request),
  ...                                 name="rmlsample.pdf")

and create the PDF:

  >>> contents() #doctest: +ELLIPSIS
  '%PDF-1.3...'


ReST to PDF Resources
---------------------

Using the ``browser:rest2pdf`` directive, you simply specify an ReST file, and
the resource is available. For example, let's make a PDF out of this file:

  >>> context = xmlconfig.string("""
  ...     <configure xmlns:browser="http://namespaces.zope.org/browser">
  ...       <browser:rest2pdf
  ...           name="pdftemplate.pdf"
  ...           path="sample/rest.txt"
  ...           />
  ...     </configure>
  ...     """, context)

  >>> resource = zapi.getAdapter(TestRequest(), name="pdftemplate.pdf")
  >>> resource()
  '%PDF-1.3...'

Optionally, you can specify your custom PDF template as well:

  >>> context = xmlconfig.string("""
  ...     <configure xmlns:browser="http://namespaces.zope.org/browser">
  ...       <browser:rest2pdf
  ...           name="pdftemplate2.pdf"
  ...           path="sample/rest.txt"
  ...           template="sample/rest_template.pt"
  ...           />
  ...     </configure>
  ...     """, context)

  >>> resource = zapi.getAdapter(TestRequest(), name="pdftemplate2.pdf")
  >>> resource() #doctest: +ELLIPSIS
  '%PDF-1.3...'

But be careful, the template needs to contain specially named styles, so that
not any arbitrary template will work:

  >>> context = xmlconfig.string("""
  ...     <configure xmlns:browser="http://namespaces.zope.org/browser">
  ...       <browser:rest2pdf
  ...           name="pdftemplate3.pdf"
  ...           path="sample/rest.txt"
  ...           template="sample/generic_template.pt"
  ...           />
  ...     </configure>
  ...     """, context)

  >>> resource = zapi.getAdapter(TestRequest(), name="pdftemplate3.pdf")
  >>> resource()
  Traceback (most recent call last):
  ...
      style = self.styleSheet[in_style]
  KeyError: 'h1'

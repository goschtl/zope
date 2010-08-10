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

  >>> import zope.component
  >>> from zope.publisher.browser import TestRequest
  >>> from zope.configuration import xmlconfig
  >>> context = xmlconfig.file('meta.zcml', package=z3c.pdftemplate)


Using ``z3c.rml`` and ReportLab to generate PDF Views
-----------------------------------------------------

See DEPENDENCIES.cfg, this lib depends on some 3rd party libraries.


Purpose: PDF-Generration with the help of ``z3c.rml`` (an open source
implementation of RML) and Reportlab. The ``z3c.rml`` is really a dialect of
the official RML and supports many more features, such as charting while still
remaining compatible with the commercial version of RML as much as possible.

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
  ...           template="sample/rml_contents.pt"
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

  >>> contents = zope.component.getMultiAdapter((folder, request),
  ...                                           name="rmlsample.pdf")

and create the PDF:

  >>> contents() #doctest: +ELLIPSIS
  '%PDF-1.3...'



Defining documents
==================

A document represents a specific document that a user might request from the
system. This can be e.g. the terms and conditions of a service, a contract, an
invoice, etc.

The developer provides a basic page template that renders RML and that can
include other blocks of RML given by the application. This can be used to
allow administrators to locally adjust the developer templates with additional
text that are specific to the installation.

Additionally the developer provides a set of fields that can be used to
customize the document on a per-document basis, e.g. with the client's name.

  >>> from z3c.rmldocument.document import Document, DocumentPageTemplateFile
  >>> import zope.interface
  >>> import zope.schema

  >>> class IContractBlocks(zope.interface.Interface):
  ...     introduction = zope.schema.Text(title=u"Introductory text")

  >>> class IContractData(zope.interface.Interface):
  ...     salutation = zope.schema.TextLine(title=u"Salutation")
  ...     years = zope.schema.Int(title=u"Years to go")

  >>> class Contract(object):
  ...     zope.interface.implements(IContractBlocks, IContractData)
  ...     introduction = """<para>
  ...         Everything will be fine in <doc:data field="years">Jahre seit Foo</doc:data> years.
  ...         </para>"""
  ...     salutation = u"Mr. Steve"
  ...     years = 4

  >>> class ServiceContract(Document):
  ...
  ...     template = DocumentPageTemplateFile(EXAMPLE % 1)
  ...
  ...     block_schema = IContractBlocks
  ...     data_schema = IContractData

Out of this document, we can produce RML that can be rendered into PDF later:

  >>> theuni = Contract()
  >>> contract_theuni = ServiceContract(theuni)
  >>> print contract_theuni(raw=True)
  <?xml version="1.0" encoding="utf-8" standalone="no"?>
  <!DOCTYPE document SYSTEM "rml.dtd">
  <document filename="service-contract.pdf">
    <template>
      <pageTemplate id="main">
        <frame id="first" x1="1cm" y1="1cm" width="19cm" height="26cm"/>
      </pageTemplate>
    </template>
    <story>
      <heading>Mr. Steve</heading>
      <para>
        Everything will be fine in 4 years.
      </para>
      <para>Best regards,<br/>Peter</para>
    </story>
  </document>



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


  >>> import z3c.rmldocument.document
  >>> import zope.interface
  >>> service_contract = z3c.rmldocument.document.Document(
  ...     template="""<?xml version="1.0" encoding="iso-8859-1" standalone="no"?>
  ...                <!DOCTYPE document SYSTEM "rml.dtd">
  ...                <document
  ...                  filename="tag-para.pdf">
  ...                  <template>
  ...                    <pageTemplate id="main">
  ...                      <frame id="first" x1="1cm" y1="1cm" width="19cm" height="26cm"/>
  ...                    </pageTemplate>
  ...                  </template>
  ...                  <story>
  ...                    <para>Foo</para>
  ...                  </story>
  ...                </document>""")


Rendering documents
===================

The document is a rather dull object. A rendering utility takes care of
actually rendering the template:

  >>> from z3c.rmldocument.renderer import Renderer
  >>> renderer = Renderer()
  >>> renderer.render(service_contract)
  '%PDF...'

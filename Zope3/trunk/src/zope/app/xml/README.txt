=======================
Zope 3 XML Architecture
=======================

Short description of the Zope 3 XML Architecture:

  * Framework to represent any object as XML (IXMLSource).

  * XML Schema Interfaces. An IXMLSource implements zero or
    more XML Schema Interfaces on a per-instance basis.

  * Using XML Schema Interfaces, we can leverage Zope 3's Component
    Architecture. There is a special kind of adapter, an XSLTAdapter,
    that can be used to adapt from one XML Schema Interface to
    another. Multiple adapters can be strung together this way to
    create a pipelined transformation architecture.

  * We can also provide views for XML source objects based on the
    schemas they implement, for instance an IXSLTView that uses an
    XSLT stylesheet to provide a presentation in HTML.

IXMLSource

  Promises to be adaptable to one of the following (these are all
  IXMLSource as well):

    * IXMLText: XML text

    * IXMLDom: W3C DOM tree.

    * IXMLSax: SAX events.

    * Potentially other representations in the future.

XML Schema Interfaces

  We can define XML schema interfaces in ZCML, as follows::

    <zopexml:schemaInterface
        uri="http://xml.zope.org/hypothetical/invoice.xsd"
    />

  The URI for the zopexml namespace is http://namespaces.zope.org/zope-xml.

  This schema interface defines no methods. In order to provide a Pythonic API
  for these invoices (IInvoice) you can do one of two things:

    * provide an adapter from IInvoiceSchema to IInvoice.

    * create a class that implements IInvoice as well as
      IXMLSource. The only XML this object should represent should be
      conformant to IInvoiceSchema.

Views

  Since XML schema interfaces can be treated like any other interfaces
  in many ways, we can also define views for them. Using the above
  example schema, the following browser page would be a view for XML
  sources implementing it::

    <browser:page
        name="report.html"
        for="http://xml.zope.org/hypothetical/invoice.xsd"
        template="report-invoice.pt"
        permission="zope.View" />

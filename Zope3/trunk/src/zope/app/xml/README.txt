=======================
Zope 3 XML Architecture
=======================

Short description of the Zope 3 XML Architecture:

  * Framework to represent any object as XML (IXMLRepresentable).

  * XML Schema Interfaces. An IXMLRepresentable implements zero or
    more XML Schema Interfaces on a per-instance basis.

  * Using XML Schema Interfaces, we can leverage Zope 3's Component
    Architecture. There is a special kind of adapter, an XSLTAdapter,
    that can be used to adapt from one XML Schema Interface to
    another. Multiple adapters can be strung together this way to
    create a pipelined transformation architecture.

  * We can also provide views for XML representable objects based on the
    schemas they implement, for instance an IXSLTView that uses an
    XSLT stylesheet to provide a presentation in HTML.

IXMLRepresentable

  Promises to be adaptable to one of (these are all IXMLRepresentable
  as well):

    * IXMLText: XML source text

    * IXMLDom: W3C DOM tree.

    * IXMLSax: SAX events.

    * Potentially other representations in the future.

XML Schema Interface

  We can define XML Schema Interfaces in ZCML, as follows::

    <zopexml:schemaInterface
      uri="http://xml.zope.org/hypothetical/invoice.xsd"
      id="zopeproducts.invoice.IInvoiceSchema"
    />

  This interface defines no methods. In order to provide a Pythonic
  API for these invoices (IInvoice) you can do one of two things:

    * provide an adapter from IInvoiceSchema to IInvoice.

    * create a class that implements IInvoice as well as
      IXMLRepresentable. The only XML this object should represent
      should be conformant to IInvoiceSchema.

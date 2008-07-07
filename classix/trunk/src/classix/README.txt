Classix
*******

Introduction
============

Classix is a thin layer over lxml's `custom element classes`_
functionality that lets you configure them declaratively. It uses
Martian_ to accomplish this effect, but to you this should be an
implementation detail.

.. _`custom element classes`: http://codespeak.net/lxml/element_classes.html

.. _`Martian`: http://pypi.python.org/pypi/martian

To parse an XML document you need a parser. An `XMLParser`` can be
configured with custom element classes that will be associated to the
right elements in the XML document after parsing. This way you can
enrich the content model of your XML document.

The approach
============

First we need to do the configuration for this package. This only needs to
happen once for this package. First, we need to set up a ``GrokkerRegistry``.

  >>> import martian
  >>> reg = martian.GrokkerRegistry()

Now we can grok the grokkers in this package::

  >>> from classix import meta
  >>> reg.grok('meta', meta)
  True

Now we can start using classix. You need to create an ``XMLParser``
class that you will associate your custom element classes with::

  >>> import classix
  >>> class MyParser(classix.XMLParser):
  ...     pass

Let's grok the parser::

  >>> reg.grok('MyParser', MyParser)
  True

Now you can set up classes to associate with particular elements in particular
namespaces, for that parser::

  >>> XMLNS = 'http://ns.example.com'
  >>> class Test(classix.Element):
  ...    classix.namespace(XMLNS)
  ...    classix.parser(MyParser)
  ... 
  ...    def custom_method(self):
  ...        return "The custom method"

We also need to grok this::

  >>> reg.grok('Test', Test)
  True

Now that we have it all set up, we can initialize the parser::

  >>> parser = MyParser()

Let's parse a bit of XML::

  >>> xml = '''\
  ...   <test xmlns="http://ns.example.com" />
  ...   '''
  >>> from lxml import etree
  >>> root = etree.XML(xml, parser)
  >>> root.custom_method()
  'The custom method'

No namespace
============

Sometimes you want to associate a class with an element in no
namespace at all. Do do this, you can set the namepace to None
explicitly::

  >>> reg = martian.GrokkerRegistry()
  >>> reg.grok('meta', meta)
  True

  >>> class MyParser(classix.XMLParser):
  ...     pass
  >>> reg.grok('MyParser', MyParser)
  True
  >>> class Test(classix.Element):
  ...     classix.namespace(None)
  ...     classix.parser(MyParser)
  ...     def custom_method(self):
  ...        return 'The custom method for no namespace'
  >>> reg.grok('Test', Test)
  True
  >>> parser = MyParser()
  >>> no_ns_xml = '''\
  ...   <test />
  ...   '''
  >>> root = etree.XML(no_ns_xml, parser)
  >>> root.custom_method()
  'The custom method for no namespace'

When supplied with an element with a namespace, the ``Test`` class will
not be associated with that element::

  >>> root = etree.XML(xml, parser)
  >>> root.custom_method()
  Traceback (most recent call last):
    ...
  AttributeError: 'lxml.etree._Element' object has no attribute 'custom_method'

Namespaces are assumed to be ``None`` if the ``classix.namespace``
directive isn't used at all::

  >>> class MyParser(classix.XMLParser):
  ...     pass
  >>> reg.grok('MyParser', MyParser)
  True
  >>> class Test(classix.Element):
  ...     classix.parser(MyParser)
  ...     def custom_method(self):
  ...        return 'The custom method for no namespace 2'
  >>> reg.grok('Test', Test)
  True
  >>> parser = MyParser()
  >>> no_ns_xml = '''\
  ...   <test />
  ...   '''
  >>> root = etree.XML(no_ns_xml, parser)
  >>> root.custom_method()
  'The custom method for no namespace 2'

Namespaces in parser
====================

As a convenience, you can also configure the default namespace in the
parser, as a fall-back so you don't have to specify it in all the
element classes::

  >>> reg = martian.GrokkerRegistry()
  >>> reg.grok('meta', meta)
  True

  >>> class MyParserWithNamespace(classix.XMLParser):
  ...    classix.namespace(XMLNS)
  >>> reg.grok('MyParserWithNamespace', MyParserWithNamespace)
  True
 
  >>> class Test2(classix.Element):
  ...    classix.parser(MyParserWithNamespace)
  ...    classix.name('test') # also override name
  ...    def custom_method(self):
  ...        return "Another custom method"
  >>> reg.grok('Test2', Test2)
  True
 
  >>> parser_ns = MyParserWithNamespace()
  >>> root = etree.XML(xml, parser_ns)
  >>> root.custom_method()
  'Another custom method'

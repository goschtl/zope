====================
XMLRPC Introspection
====================

This Zope 3 package provides an xmlrpcintrospection mechanism,
as defined here:

    http://xmlrpc-c.sourceforge.net/xmlrpc-howto/xmlrpc-howto-api-introspection.html

It registers three new xmlrpc methods:

    - `listMethods()`: Lists all xmlrpc methods (ie views) registered for the current object

    - `methodHelp(method_name)`: Returns the method documentation of the given method.

    - `methodSignature(method_name)`: Returns the method documentation of the given method.

It is based on introspection mechanisms provided by the apidoc package.

***** xmlrpc reminder *****

Let's write a view that returns a folder listing:

  >>> class FolderListing:
  ...     def contents(self):
  ...         return list(self.context.keys())

Now we'll register it as a view:

  >>> from zope.configuration import xmlconfig
  >>> ignored = xmlconfig.string("""
  ... <configure
  ...     xmlns="http://namespaces.zope.org/zope"
  ...     xmlns:xmlrpc="http://namespaces.zope.org/xmlrpc"
  ...     >
  ...   <!-- We only need to do this include in this example,
  ...        Normally the include has already been done for us. -->
  ...   <include package="zope.app.publisher.xmlrpc" file="meta.zcml" />
  ...
  ...   <xmlrpc:view
  ...       for="zope.app.folder.folder.IFolder"
  ...       methods="contents"
  ...       class="zope.app.xmlrpcintrospection.README.FolderListing"
  ...       permission="zope.ManageContent"
  ...       />
  ... </configure>
  ... """)

Now, we'll add some items to the root folder:

  >>> print http(r"""
  ... POST /@@contents.html HTTP/1.1
  ... Authorization: Basic bWdyOm1ncnB3
  ... Content-Length: 73
  ... Content-Type: application/x-www-form-urlencoded
  ...
  ... type_name=BrowserAdd__zope.app.folder.folder.Folder&new_value=f1""")
  HTTP/1.1 303 See Other
  ...

  >>> print http(r"""
  ... POST /@@contents.html HTTP/1.1
  ... Authorization: Basic bWdyOm1ncnB3
  ... Content-Length: 73
  ... Content-Type: application/x-www-form-urlencoded
  ...
  ... type_name=BrowserAdd__zope.app.folder.folder.Folder&new_value=f2""")
  HTTP/1.1 303 See Other
  ...

And call our xmlrpc method:

  >>> print http(r"""
  ... POST / HTTP/1.0
  ... Authorization: Basic bWdyOm1ncnB3
  ... Content-Length: 102
  ... Content-Type: text/xml
  ...
  ... <?xml version='1.0'?>
  ... <methodCall>
  ... <methodName>contents</methodName>
  ... <params>
  ... </params>
  ... </methodCall>
  ... """)
  HTTP/1.0 200 Ok
  Content-Length: 208
  Content-Type: text/xml;charset=utf-8
  <BLANKLINE>
  <?xml version='1.0'?>
  <methodResponse>
  <params>
  <param>
  <value><array><data>
  <value><string>f1</string></value>
  <value><string>f2</string></value>
  </data></array></value>
  </param>
  </params>
  </methodResponse>
  <BLANKLINE>

***** end of xmlrpc reminder *****

Now we want to provide to that view introspection.
Let's add three new xmlrcp methods, that published
the introspection api.

  >>> ignored = xmlconfig.string("""
  ... <configure
  ...     xmlns="http://namespaces.zope.org/zope"
  ...     xmlns:xmlrpc="http://namespaces.zope.org/xmlrpc"
  ...     >
  ...   <!-- We only need to do this include in this example,
  ...        Normally the include has already been done for us. -->
  ...   <include package="zope.app.publisher.xmlrpc" file="meta.zcml" />
  ...   <xmlrpc:view
  ...     for="zope.interface.Interface"
  ...     methods="listAllMethods  methodHelp methodSignature"
  ...     class="zope.app.xmlrpcintrospection.xmlrpcintrospection.XMLRPCIntrospection"
  ...     permission="zope.Public"
  ...     />
  ... </configure>
  ... """)

They are linked to XMLRPCIntrospection class, that actually
 knows how to lookup to all interfaces

And call our xmlrpc method, that should list the content method:

  >>> print http(r"""
  ... POST / HTTP/1.0
  ... Content-Type: text/xml
  ...
  ... <?xml version='1.0'?>
  ... <methodCall>
  ... <methodName>listAllMethods</methodName>
  ... <params>
  ... </params>
  ... </methodCall>
  ... """, handle_errors=False)
  HTTP/1.0 200 Ok
  Content-Length: ...
  Content-Type: text/xml...
  <BLANKLINE>
  <?xml version='1.0'?>
  <methodResponse>
  <params>
  <param>
  <value><array><data>
  <value><string>contents</string></value>
  </data></array></value>
  </param>
  </params>
  </methodResponse>
  <BLANKLINE>

Let's try to add another method, to se if it gets listed...

  >>> class FolderListing2:
  ...     def contents2(self):
  ...         return list(self.context.keys())
  >>> from zope.configuration import xmlconfig
  >>> ignored = xmlconfig.string("""
  ... <configure
  ...     xmlns="http://namespaces.zope.org/zope"
  ...     xmlns:xmlrpc="http://namespaces.zope.org/xmlrpc"
  ...     >
  ...   <!-- We only need to do this include in this example,
  ...        Normally the include has already been done for us. -->
  ...   <include package="zope.app.publisher.xmlrpc" file="meta.zcml" />
  ...
  ...   <xmlrpc:view
  ...       for="zope.app.folder.folder.IFolder"
  ...       methods="contents2"
  ...       class="zope.app.xmlrpcintrospection.README.FolderListing2"
  ...       permission="zope.ManageContent"
  ...       />
  ... </configure>
  ... """)
  >>> print http(r"""
  ... POST / HTTP/1.0
  ... Content-Type: text/xml
  ...
  ... <?xml version='1.0'?>
  ... <methodCall>
  ... <methodName>listAllMethods</methodName>
  ... <params>
  ... </params>
  ... </methodCall>
  ... """, handle_errors=False)
  HTTP/1.0 200 Ok
  Content-Length: ...
  Content-Type: text/xml...
  <BLANKLINE>
  <?xml version='1.0'?>
  <methodResponse>
  <params>
  <param>
  <value><array><data>
  <value><string>contents</string></value>
  <value><string>contents2</string></value>
  </data></array></value>
  </param>
  </params>
  </methodResponse>
  <BLANKLINE>



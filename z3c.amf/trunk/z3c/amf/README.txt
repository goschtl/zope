AMF/Flash Support in Zope 2
===========================

Introduction
------------

This package allows you to query Zope 2 from a flash using Flex with
Actionscript 2 or Actionscript 3 throught AMF0 or AMF3.

We are just providing here the Zope layer. The lower layer has been done
using the PyAMF package (see http://pyamf.org).

Let's write a simple AMF view that echoes various types of input:

  >>> from Products.Five import BrowserView
  >>> from datetime import datetime
  >>> import elementtree.ElementTree as etree
  >>> class EchoView(BrowserView):
  ...
  ...   def echoString(self, value):
  ...       return "%s" % value
  ...
  ...   def echoProtectedString(self, value):
  ...       return "%s" % value
  ...
  ...   def echoList(self, value):
  ...       return list(value)
  ...
  ...   def echoDict(self, value):
  ...       return dict(value)
  ...
  ...   def echoVoid(self, value):
  ...       pass
  ...
  ...   def echoTuple(self, value):
  ...       return tuple(value)
  ...
  ...   def echoDate(self):
  ...       return datetime(2008, 11, 17, 11, 11)
  ...
  ...   def echoXML(self, value):
  ...       root = etree.Element("html")
  ...       body = etree.SubElement(root, 'body')
  ...       body.text = value
  ...       return root

Now we'll register it as a Flash view. For now we'll just register the
view for folder objects and call it on the default folder of the user:

  >>> from zope.configuration import xmlconfig
  >>> ignored = xmlconfig.string("""
  ... <configure
  ...     xmlns="http://namespaces.zope.org/zope"
  ...     xmlns:browser="http://namespaces.zope.org/browser"
  ...     xmlns:flash="http://namespaces.zope.org/flash"
  ...     >
  ...
  ...   <include package="z3c.amf" file="meta.zcml" />
  ...   <include package="Products.Five" file="meta.zcml" />
  ...   <include package="z3c.amf" />
  ...
  ...   <flash:view
  ...       for="OFS.interfaces.IFolder"
  ...       methods="echoString echoList echoDict echoVoid echoTuple
  ...                echoDate echoXML"
  ...       class="z3c.amf.README.EchoView"
  ...       permission="zope.Public"
  ...       />
  ...
  ...   <flash:view
  ...       for="OFS.interfaces.IFolder"
  ...       methods="echoProtectedString"
  ...       class="z3c.amf.README.EchoView"
  ...       permission="zope2.FlashAccess"
  ...       />
  ...
  ... </configure>
  ... """)

We create some helper functions.
For Requests:

  >>> def createAMFRequest(target, body, username=None, password=None):
  ...   envelope = remoting.Envelope(pyamf.AMF0, pyamf.ClientTypes.Flash9)
  ...   if username is not None and password is not None:
  ...       envelope.headers['Credentials'] = dict(userid=unicode(username),
  ...                                              password=unicode(password))
  ...   request = remoting.Request(target, [body], envelope)
  ...   envelope[u'/1'] = request
  ...   amfRequest = remoting.encode(envelope)
  ...   amfRequest.seek(0)
  ...   return amfRequest.read()

For Responses:

  >>> import pyamf
  >>> from pyamf import remoting
  >>> def printAMFResponse(response):
  ...   context = pyamf.amf0.Context
  ...   requests = remoting.decode(response.body, context())
  ...   for name, value in requests.items():
  ...       print (name, value, type(value.body))

Basic Types
-----------

String

  >>> amfRequest = createAMFRequest(target='echoString', body='Hello World!')
  >>> amfRequest
  '\x00\x03\x00\x00\x00\x01\x00\nechoString\x00\x02/1\x00\x00\x00\x00\n\x00\x00\x00\x01\x02\x00\x0cHello World!'
  >>> response = http(r"""
  ... POST /test_folder_1_ HTTP/1.0
  ... Content-Length: 102
  ... Content-Type: application/x-amf
  ...
  ... %s""" % amfRequest)
  >>> printAMFResponse(response)
  (u'/1', <Response status=/onResult>Hello World!</Response>, <type 'unicode'>)

List

  >>> amfRequest = createAMFRequest(target='echoList', body=[u'Hé', u'Ho'])
  >>> response = http(r"""
  ... POST /test_folder_1_ HTTP/1.0
  ... Content-Length: 102
  ... Content-Type: application/x-amf
  ...
  ... %s""" % amfRequest)
  >>> printAMFResponse(response)
  (u'/1', <Response status=/onResult>[u'H\xc3\xa9', u'Ho']</Response>,
   <type 'list'>)

Dictionary

  >>> amfRequest = createAMFRequest(target='echoDict',
  ...                               body={'fruit': 'orange'})
  >>> response = http(r"""
  ... POST /test_folder_1_ HTTP/1.0
  ... Content-Length: 102
  ... Content-Type: application/x-amf
  ...
  ... %s""" % amfRequest)
  >>> printAMFResponse(response)
  (u'/1', <Response status=/onResult>{u'fruit': u'orange'}</Response>,
   <class 'pyamf.ASObject'>)

Without return

  >>> amfRequest = createAMFRequest(target='echoVoid', body='Hello World!')
  >>> response = http(r"""
  ... POST /test_folder_1_ HTTP/1.0
  ... Content-Length: 102
  ... Content-Type: application/x-amf
  ...
  ... %s""" % amfRequest)
  >>> printAMFResponse(response)
  (u'/1', <Response status=/onResult>None</Response>, <type 'NoneType'>)

Tuple

  >>> amfRequest = createAMFRequest(target='echoTuple', body=['foo', 'bar'])
  >>> response = http(r"""
  ... POST /test_folder_1_ HTTP/1.0
  ... Content-Length: 102
  ... Content-Type: application/x-amf
  ...
  ... %s""" % amfRequest)
  >>> printAMFResponse(response)
  (u'/1', <Response status=/onResult>[u'foo', u'bar']</Response>,
   <type 'list'>)

Datetime

  >>> amfRequest = createAMFRequest(target='echoDate', body=None)
  >>> response = http(r"""
  ... POST /test_folder_1_ HTTP/1.0
  ... Content-Length: 102
  ... Content-Type: application/x-amf
  ...
  ... %s""" % amfRequest)
  >>> printAMFResponse(response)
  (u'/1', <Response status=/onResult>2008-11-17 11:11:00</Response>,
   <type 'datetime.datetime'>)

XML

  >>> amfRequest = createAMFRequest(target='echoXML', body='It works!')
  >>> response = http(r"""
  ... POST /test_folder_1_ HTTP/1.0
  ... Content-Length: 102
  ... Content-Type: application/x-amf
  ...
  ... %s""" % amfRequest)
  >>> printAMFResponse(response)
  (u'/1', <Response status=/onResult><Element html at ...></Response>,
   <type 'instance'>)

Errors
------


  >>> amfRequest = createAMFRequest(target='echoUnknown', body=['foo', 'bar'])
  >>> response = http(r"""
  ... POST /test_folder_1_ HTTP/1.0
  ... Content-Length: 102
  ... Content-Type: application/x-amf
  ...
  ... %s""" % amfRequest)
  >>> printAMFResponse(response)
  (u'/1', <Response status=/onStatus><ErrorFault level=error code=NotFound type=Resource not found...
  ...


User authentication
-------------------

Try to access our protected view without providing login/pass in flash:

  >>> amfRequest = createAMFRequest(target='echoProtectedString',
  ...                               body='It works!')
  >>> response = http(r"""
  ... POST /test_folder_1_ HTTP/1.0
  ... Content-Length: 102
  ... Content-Type: application/x-amf
  ...
  ... %s""" % amfRequest)
  >>> printAMFResponse(response)
  (u'/1', <Response status=/onStatus><ErrorFault level=error code=zExceptions.unauthorized.Unauthorized type=Not authorized></Response>,
   <class 'pyamf.remoting.ErrorFault'>)


Now try to access with login/pass:

  >>> from Testing.ZopeTestCase import user_name, user_password
  >>> amfRequest = createAMFRequest(target='echoProtectedString',
  ...                               body="Hello World!", username=user_name,
  ...                               password=user_password)
  >>> response = http(r"""
  ... POST /test_folder_1_ HTTP/1.0
  ... Content-Length: 200
  ... Content-Type: application/x-amf
  ...
  ... %s""" % amfRequest)
  >>> printAMFResponse(response)
  (u'/1', <Response status=/onResult>Hello World!</Response>, <type 'unicode'>)

============
JSONRPC Tree
============

This package offers a JSONRPC tree view which can be used as navigation tree.
Let's show how we can register our jsonrpc tree view:

  >>> from zope.configuration import xmlconfig
  >>> import z3c.jsonrpc
  >>> context = xmlconfig.file('meta.zcml', z3c.jsonrpc)
  >>> context = xmlconfig.string("""
  ... <configure
  ...     xmlns:z3c="http://namespaces.zope.org/z3c">
  ...   <z3c:jsonrpc
  ...       for="*"
  ...       class="z3c.jsontree.jsonrpc.JSONTreeItems"
  ...       permission="zope.Public"
  ...       methods="loadJSONTreeItems"
  ...       layer="z3c.jsonrpc.testing.IJSONRPCTestSkin"
  ...       />
  ... </configure>
  ... """, context)

Now we will setup some content structure based on the default zope folder class:

  >>> from zope.site.folder import Folder
  >>> site  = getRootFolder()
  >>> content = Folder()
  >>> site['content'] = content

And we need to be able to get an absoluteURL for the form:

  >>> import zope.interface
  >>> import zope.component
  >>> from zope.location.interfaces import ILocation
  >>> from zope.traversing.browser.interfaces import IAbsoluteURL
  >>> class FakeURL(object):
  ...     zope.interface.implements(IAbsoluteURL)
  ...     zope.component.adapts(ILocation, zope.interface.Interface)
  ...     def __init__(self, context, request):
  ...         pass
  ...     def __str__(self):
  ...         return u'http://fake/url'
  ...     def __call__(self):
  ...         return str(self)

  >>> zope.component.provideAdapter(FakeURL)


JSON-RPC proxy
--------------

If we call our JSON-RPC tree item method, we can see the different JSON data
on the different contexts:

  >>> from z3c.jsonrpc.testing import JSONRPCTestProxy
  >>> siteURL = 'http://localhost/++skin++JSONRPCTestSkin'
  >>> proxy = JSONRPCTestProxy(siteURL)
  >>> proxy.loadJSONTreeItems('z3cJSONTree')
  {u'treeChilds': {u'childs':
  [{u'hasChilds': False,
    u'contextURL': u'http://fake/url',
    u'url': u'http://fake/url/@@SelectedManagementView.html',
    u'linkHandler': u'',
    u'content': u'content',
    u'iconURL': u'',
    u'id': u'z3cJSONTree.::content'}],
    u'id': u'z3cJSONTree'}}

The content object has no items and returns some empty JSON data:

  >>> proxy = JSONRPCTestProxy(siteURL + '/content')
  >>> proxy.loadJSONTreeItems('z3cJSONTree')
  {u'treeChilds': {u'childs': [], u'id': u'z3cJSONTree'}}

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

  >>> from zope.app.folder.folder import Folder
  >>> site  = getRootFolder()
  >>> content = Folder()
  >>> site['content'] = content


JSON-RPC proxy
--------------

If we call our JSON-RPC tree item method, we can see the different JSON data
on the different contexts:

  >>> from z3c.jsonrpc.testing import JSONRPCTestProxy
  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> browser.addHeader('Accept-Language', 'en')
  >>> browser.addHeader('Content-Type', 'application/json')
  >>> siteURL = 'http://localhost/++skin++JSONRPCTestSkin'
  >>> proxy = JSONRPCTestProxy(siteURL)
  >>> proxy.loadJSONTreeItems('z3cJSONTree')
  {u'treeChilds': {u'childs':
  [{u'hasChilds': False,
    u'contextURL': u'http://localhost/++skin++JSONRPCTestSkin/content',
    u'url': u'http://localhost/++skin++JSONRPCTestSkin/content/@@SelectedManagementView.html',
    u'linkHandler': u'', u'content': u'content', u'iconURL': u'', u'id':
    u'z3cJSONTree.::content'}],
    u'id': u'z3cJSONTree'}}

The content object has no items and returns some empty JSON data:

  >>> proxy = JSONRPCTestProxy(siteURL + '/content')
  >>> proxy.loadJSONTreeItems('z3cJSONTree')
  {u'treeChilds': {u'childs': [], u'id': u'z3cJSONTree'}}

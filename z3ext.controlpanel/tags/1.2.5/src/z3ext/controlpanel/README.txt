=============
Control Panel
=============

In many cases programm modules needs configuration and some common way
of managing configuration. Control panel very similar with zope.app.preference,
it stores all data in site annotation, in BTrees. so you can removeing 
and add any configlet without problem with zodb.

We need load zcml configuration::

  >>> from zope.configuration import xmlconfig
  >>> import z3ext.controlpanel
  >>> context = xmlconfig.file('meta.zcml', z3ext.controlpanel)

  >>> from zope import interface, component, schema
  >>> from z3ext.controlpanel import interfaces

We can register configlet with `z3ext:configlet` directive.

Let's create simple configlet. First we need define configlet schema:

  >>> class ITestConfiglet1(interface.Interface):
  ...     
  ...     param1 = schema.TextLine(
  ...         title = u'param1',
  ...         default = u'default param1')
  ...     
  ...     param2 = schema.Int(
  ...         title = u'param2',
  ...         default = 10)

Now configlet registration:

  >>> context = xmlconfig.string("""
  ... <configure xmlns:z3ext="http://namespaces.zope.org/z3ext"
  ...    i18n_domain="zope">
  ...   <z3ext:configlet
  ...	   name="configlet1"
  ...      schema="z3ext.controlpanel.README.ITestConfiglet1"
  ...      title="Test configlet1"
  ...      description="Test configlet1 description" />
  ... </configure>""", context)

That's all. now we can get configlet as utility.

As named IConfiglet

  >>> cl = component.getUtility(interfaces.IConfiglet, name='configlet1')
  >>> cl.__name__ == 'configlet1'
  True
  >>> cl.__title__ == 'Test configlet1'
  True
  >>> cl.__description__ == 'Test configlet1 description'
  True

As schema utility

  >>> cl1 = component.getUtility(ITestConfiglet1)
  >>> cl is cl1
  True

  >>> cl.__schema__
  <InterfaceClass z3ext.controlpanel.README.ITestConfiglet1>

We can't change __schema__ at runtime

  >>> cl.__schema__ = ITestConfiglet1
  Traceback (most recent call last):
  ...
  AttributeError: Can't set __schema__


IConfiglet
----------

Let's access configlet attributes:

  >>> cl.param1
  u'default param1'

  >>> cl.param2
  10

which is the default value, since we have not set it yet. We can now reassign
the value:

  >>> cl.param1 = u'test'
  >>> cl.param1
  u'test'

However, you cannot just enter any value, since it is validated before the
assignment:

  >>> cl.param2 = 'str'
  Traceback (most recent call last):
  ...
  WrongType: ...

You can delete attribute, default value would restored

  >>> del cl.param1
  >>> cl.param1
  u'default param1'

You can set/remove any attributes to configlet, but this attributes won't 
be persistent.

  >>> cl.test = 1
  >>> cl.test
  1

  >>> del cl.test

Configlet is ILocation object so it can't be used in traversing

  >>> cl.__parent__
  <z3ext.controlpanel.root.RootConfiglet object at ...>

  >>> cl.__name__
  u'configlet1'
  
  >>> from zope.traversing.api import getPath
  >>> getPath(cl)
  u'/settings/configlet1'


Configlet security
------------------

Read/Write access to configlet same as for <class> directive. By default
all fields in IConfiglet interface and schema protected by 'z3ext.Configure'
permission. We can define default permission in 'permission' attribute.
We can use <require/> and <allow/> subdirectives inside <z3ext:configlet>
directive.

  >>> class ITestConfiglet2(interface.Interface):
  ...     
  ...     param1 = schema.TextLine(
  ...         title = u'param1',
  ...         default = u'default param1')
  ...     
  ...     param2 = schema.Int(
  ...         title = u'param2',
  ...         default = 10)
  ...     
  ...     param3 = schema.TextLine(
  ...         title = u'param3',
  ...         default = u'default param3')

  >>> xmlconfig.string("""
  ... <configure xmlns:z3ext="http://namespaces.zope.org/z3ext"
  ...    i18n_domain="zope">
  ...   <include package="z3ext.controlpanel" file="meta.zcml" />
  ...   <z3ext:configlet
  ...	    name="configlet2"
  ...      schema="z3ext.controlpanel.README.ITestConfiglet2"
  ...      title="Test configlet2"
  ...      permission="zope.Public">
  ...    <require />
  ...   </z3ext:configlet>
  ... </configure>""")
  Traceback (most recent call last):
  ...
  ZopeXMLConfigurationError: ...Nothing required...

  >>> xmlconfig.string("""
  ... <configure xmlns:z3ext="http://namespaces.zope.org/z3ext"
  ...    i18n_domain="zope">
  ...   <include package="z3ext.controlpanel" file="meta.zcml" />
  ...   <z3ext:configlet
  ...	    name="configlet2"
  ...      schema="z3ext.controlpanel.README.ITestConfiglet2"
  ...      title="Test configlet2"
  ...      permission="zope.Public">
  ...    <require attributes="param1" />
  ...   </z3ext:configlet>
  ... </configure>""")
  Traceback (most recent call last):
  ...
  ZopeXMLConfigurationError: ...No permission specified...

  >>> context = xmlconfig.string("""
  ... <configure xmlns:z3ext="http://namespaces.zope.org/z3ext"
  ...    i18n_domain="zope">
  ...   <include package="z3ext.controlpanel" file="meta.zcml" />
  ...   <z3ext:configlet
  ...	    name="configlet2"
  ...      schema="z3ext.controlpanel.README.ITestConfiglet2"
  ...      title="Test configlet2"
  ...      permission="zope.Public">
  ...    <require attributes="param1" permission="zope.Public" />
  ...    <allow attributes="param2" />
  ...    <require set_attributes="param3" permission="zope.Public" />
  ...   </z3ext:configlet>
  ... </configure>""", context)


Custom class implementation
---------------------------

We can use custom configlet implementation

  >>> class TestConfiglet1(object):
  ...     pass

  >>> context = xmlconfig.string("""
  ... <configure xmlns:z3ext="http://namespaces.zope.org/z3ext"
  ...    i18n_domain="zope">
  ...   <include package="z3ext.controlpanel" file="meta.zcml" />
  ...   <z3ext:configlet
  ...	    name="configlet3"
  ...      class="z3ext.controlpanel.README.TestConfiglet1"
  ...      schema="z3ext.controlpanel.README.ITestConfiglet2"
  ...      title="Test configlet3">
  ...   </z3ext:configlet>
  ... </configure>""")

  >>> configlet = component.getUtility(interfaces.IConfiglet, 'configlet3')
  >>> isinstance(configlet, TestConfiglet1)
  True


Configlet groups
----------------

The configlet would not be very powerful, if you could create a full
settingss. So let's create a sub-configlet for settings:

  >>> len(configlet)
  0

  >>> 'configlet' in configlet
  False

  >>> configlet.get('configlet') is None
  True

  >>> configlet['configlet']
  Traceback (most recent call last):
  ...
  KeyError: 'configlet'

  >>> context = xmlconfig.string("""
  ... <configure xmlns:z3ext="http://namespaces.zope.org/z3ext"
  ...    i18n_domain="zope">
  ...   <include package="z3ext.controlpanel" file="meta.zcml" />
  ...   <z3ext:configlet
  ...	    name="configlet3.configlet"
  ...      schema="z3ext.controlpanel.README.ITestConfiglet1"
  ...      title="Test configlet4">
  ...   </z3ext:configlet>
  ... </configure>""", context)

  >>> configlet['configlet'].__parent__ is configlet
  True

  >>> len(configlet)
  1

  >>> 'configlet' in configlet
  True

  >>> configlet['configlet'].__id__
  u'configlet3.configlet'

  >>> configlet.items()
  [(u'configlet', <z3ext.controlpanel.configlettype.Configlet<configlet3.configlet> ...)]

  >>> configlet.values()
  [<z3ext.controlpanel.configlettype.Configlet<configlet3.configlet> ...>]

  >>> list(iter(configlet))
  [<z3ext.controlpanel.configlettype.Configlet<configlet3.configlet> ...>]


Configlet availability
----------------------

We can check availability

  >>> def testConfiglet1(configlet):
  ...     return True

  >>> def testConfiglet2(configlet):
  ...     return False

  >>> c1 = configlet['configlet']
  >>> c1.isAvailable()
  True

  >>> c1.__tests__ = (testConfiglet2,)
  >>> c1.isAvailable()
  False

Avialability automaticly checks in parent configlet

  >>> c1.__tests__ = (testConfiglet1,)
  >>> c1.isAvailable()
  True

  >>> configlet.__tests__ = (testConfiglet2,)

  >>> c1.isAvailable()
  False

  >>> c1.__tests__ = (testConfiglet1, testConfiglet2)
  >>> c1.isAvailable()
  False

  >>> configlet.remove('configlet')
  >>> len(configlet)
  0

We can add custom availability checks in z3ext:configlet directory

  >>> t = xmlconfig.string("""
  ... <configure xmlns:z3ext="http://namespaces.zope.org/z3ext"
  ...    i18n_domain="zope">
  ...   <include package="z3ext.controlpanel" file="meta.zcml" />
  ...   <z3ext:configlet
  ...	   name="configlet"
  ...      schema="z3ext.controlpanel.README.ITestConfiglet1"
  ...      tests="z3ext.controlpanel.README.testConfiglet1"
  ...      title="Test configlet">
  ...   </z3ext:configlet>
  ... </configure>""")

It should be callable

  >>> test = False
  >>> t = xmlconfig.string("""
  ... <configure xmlns:z3ext="http://namespaces.zope.org/z3ext"
  ...    i18n_domain="zope">
  ...   <include package="z3ext.controlpanel" file="meta.zcml" />
  ...   <z3ext:configlet
  ...	   name="configlet"
  ...      schema="z3ext.controlpanel.README.ITestConfiglet1"
  ...      tests="z3ext.controlpanel.README.test"
  ...      title="Test configlet">
  ...   </z3ext:configlet>
  ... </configure>""")
  Traceback (most recent call last):
  ...
  ZopeXMLConfigurationError: ...


Root configlet
--------------

There is root configlet. You can access any other configlets from root configlet.
This configlet has no name, so it's available as nameless IConfiglet utility:

 >>> from zope.app.component.hooks import getSite

 >>> root = component.getUtility(interfaces.IConfiglet)
 >>> root
 <z3ext.controlpanel.root.RootConfiglet object at ...>

Root configlet parent is ISite object

 >>> root.__parent__ is getSite()
 True

 >>> ITestConfiglet1.providedBy(root['configlet1'])
 True

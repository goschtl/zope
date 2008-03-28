=========
Skin tool
=========

Skin tool allow configure skin at runtime for each ISite object.

  >>> from z3ext.skintool import interfaces, zcml
  >>> from z3ext.skintool.tool import skinToolModified

  >>> from zope import interface, component, schema

We need site object and request

  >>> from zope.app.component.hooks import getSite
  >>> site = getSite()

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()

Now let's define layer

  >>> from zope import interface
  >>> class IMyLayer(interface.Interface):
  ...     pass

Before we can use IMyLayer we should register it in local registry

  >>> zcml.layerDirective(IMyLayer, u'mylayer', u'My layer', '', ())

Now layer should be listed in vocabulary.

  >>> from z3ext.skintool.vocabulary import LayersVocabulary
  >>> voc = LayersVocabulary()(site)
  >>> term = voc.getTerm(IMyLayer)
  >>> term.value == u'mylayer'
  True
  >>> term.title == 'My layer'
  True
  >>> term.token == u'mylayer'
  True

All layers applied in IBeforeTraverseEvent event for ISite object. We will
use handler directly.

  >>> from z3ext.skintool.subscribers import threadServiceSubscriber
  >>> from zope.app.publication.interfaces import BeforeTraverseEvent

Let's check layer for our request.

  >>> threadServiceSubscriber(site, BeforeTraverseEvent(site, request))

  >>> IMyLayer.providedBy(request)
  False

This is because we should configure skin tool to use our layer and
site object should implement ISkinable interface.

  >>> interface.directlyProvides(site, interfaces.ISkinable)

Let's configure skin tool

  >>> tool = component.getUtility(interfaces.ISkinTool)
  >>> tool.user_layers = [u'mylayer']
  >>> skinToolModified()
  
Let's try again

  >>> threadServiceSubscriber(site, BeforeTraverseEvent(site, request))
  >>> IMyLayer.providedBy(request)
  True

Change layers config

  >>> tool.user_layers = []
  >>> skinToolModified()

  >>> threadServiceSubscriber(site, BeforeTraverseEvent(site, request))
  >>> IMyLayer.providedBy(request)
  False


Some layers can depends on other layers

  >>> class IMyLayer2(interface.Interface):
  ...     pass

  >>> zcml.layerDirective(IMyLayer2, u'mylayer2', u'My layer2', '', (IMyLayer,))
  >>> tool.user_layers = [u'mylayer2']
  >>> skinToolModified()

  >>> threadServiceSubscriber(site, BeforeTraverseEvent(site, request))
  >>> IMyLayer2.providedBy(request)
  True
  >>> IMyLayer.providedBy(request)
  True

We can define default layer, that will added automaticly

  >>> class IDefaultLayer(interface.Interface):
  ...     pass

We have to register utility IDefaultLayer

  >>> component.provideUtility(IDefaultLayer, interfaces.IDefaultLayer, 'default')
  >>> tool.user_layers = [u'mylayer']
  >>> skinToolModified()

  >>> threadServiceSubscriber(site, BeforeTraverseEvent(site, request))
  >>> IMyLayer.providedBy(request)
  True
  >>> IDefaultLayer.providedBy(request)
  True


z3ext:layer directive
---------------------

We can do same with z3ext:layer directive. We need load zcml file:

  >>> import z3ext.skintool
  >>> from zope.configuration import xmlconfig
  >>> context = xmlconfig.file('meta.zcml', z3ext.skintool)

  >>> context = xmlconfig.string("""
  ... <configure xmlns:z3ext="http://namespaces.zope.org/z3ext"
  ...    xmlns="http://namespaces.zope.org/zope" i18n_domain="z3ext">
  ...  <z3ext:layer
  ...    name="mylayer3"
  ...    layer="z3ext.skintool.README.IMyLayer"
  ...    title="My zcml layer" />
  ... </configure>""", context)

  >>> voc = LayersVocabulary()(site)
  >>> term = voc.getTerm(IMyLayer)
  >>> term.value == u'mylayer3'
  True
  >>> term.title == 'My zcml layer'
  True
  >>> term.token == u'mylayer3'
  True

  >>> tool.user_layers = ['mylayer3']
  >>> skinToolModified()

  >>> threadServiceSubscriber(site, BeforeTraverseEvent(site, request))
  >>> IMyLayer.providedBy(request)
  True

  >>> context = xmlconfig.string("""
  ... <configure xmlns:z3ext="http://namespaces.zope.org/z3ext"
  ...    xmlns="http://namespaces.zope.org/zope" i18n_domain="z3ext">
  ...  <z3ext:layer
  ...    name="mylayer4"
  ...    layer="z3ext.skintool.README.IMyLayer2"
  ...    title="My zcml layer4"
  ...    require="z3ext.skintool.README.IMyLayer" />
  ... </configure>""", context)

  >>> tool.user_layers = [u'mylayer2']
  >>> skinToolModified()

  >>> threadServiceSubscriber(site, BeforeTraverseEvent(site, request))
  >>> IMyLayer2.providedBy(request)
  True
  >>> IMyLayer.providedBy(request)
  True

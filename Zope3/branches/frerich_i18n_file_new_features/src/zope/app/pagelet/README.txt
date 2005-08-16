========
Pagelets
========

Definition
----------
                      _________
                     |         |
                     | Context |
                     |_________|
                          ^
                          |
                          |*
                      ____|____
                     |         |
                     |   View  |
                     |_________|
                          |
                          |
                          |* a view is composed of slots
                      ____v____
                     |          |
                     | ViewSlot |
                     |__________|
                          |
                          |
                          |* a slot contains a list of viewlets
                      ____v____        _____________
                     |         |      |             |
                     | Viewlet |------| ViewletType |
                     |_________|*     |_____________|
                          ^
                         /_\
              ____________|____________
             |                         |
         ____|____                 ____|____
        |         |               |         |
        | Pagelet |               | Portlet |
        |_________|               |_________|

A view instance is associated with one context. A context may be viewed
with none ore more views.

The distinction between Pagelet and Portlet is still fuzzy. Pagelets and
portlets are designed to be parts of a view. In that meaning pagelets
and portlets are equal. They are specialized viewlets. A view is composed
of viewlets which are related to a specific slot of that view.

But what is the difference between them? The reconstructed interpretation
of Zope's common sense is the following::

    A pagelet of a view displays the underlying context.
    A portlet of a view displays data from different contexts.

    Examples: The metadata pagelet displays the metadata of
    the underlying context. The metadata portlet displays for
    example the metadata of all its children.

    A calendar pagelet displays the calendar data of a content
    object that implements an own calendar. A calendar portlet
    displays global calendar data on different objects that may
    come from an utility for example.


In view of the component architecture this differentiation does not make
sense anymore, because the adaption mechanism hides such criteria
(implementation decisions and details) transparently inside an adapter.

That is the reason, why we try to provide a new definition::

    A pagelet of a view operates of the underlying context.
    A portlet of a view operates of the underlying or a
    different context.

    Examples: The metadata pagelet displays the metadata.
    Therefore it adapts the underlying context to IMetadata.
    The metadata portlet displays metadata too, but it adapts
    a context independently to the underlying view context.

    Hence several pagelets of the same type composed inside
    one view must display always the similar content where
    several portlets of the same type composed inside a view
    can present different contents.


Usage
-----
This pagelet implementation supports pagelets and portlets in respect of
the first definition, but it only supports pagelets in respect of the
second definition.

In the following text we us pagelet in the sense of the latter.

Pagelets are responsible for a piece of content in a view. They can be
used to render additionally provided information into a pagetemplate.

Pagelets are small, view-like components that can registered to
skin layers(request)-, contenttype-, view- and slot-interfaces.

Inside a pagetemplate of a view, the registered pagelets can be called by
the tal:pagelets command. The return value is a list of macros where each
macro correspondents to a registered pagelet. The pagelet engine always uses
the macro from the pagelet which has the same name like the pagelet itself.
This macros can be used to invoke the pagelets:

  <div class="row">
    <tal:repeat="pagelets pagelets:zope.app.demo.pagelet.interfaces.IDemoSlot">
      <tal:block metal:use-macro="pagelets" />
    </tal:repeat>
  </div>

Such a macro may process static content or invoke the context- or
view-namespace for dynamic contents::

  <div class="row">
    <h4>content:</h4>
    <span tal:content="view/title">title</span>
  </div>

The latter is not recommended, because it glues view and pagelet together.
That means a pagelet depends on a specific view- or context implementation.

In respect of modularization we provide an additional tal:pagedata
command. This command allows to look up adapters providing an interface
derived form IPageletData::

  <div class="row">
    <tal:define="data pagedata:zope.app.demo.pagelet.interfaces.IDemoPageData">
      <h4>content:</h4>
      <span tal:content="data/title">title</span>
    </tal:define>
  </div>

This is a restricted adapter invocation. It should prevent uncontrolled
adapter invocation inside pagetemplates, because that would glue view
layer and programming layer in not appreciable manner.


Let's show how to use pagelets
==============================

Imports:

  >>> import zope.component
  >>> from zope.app import zapi
  >>> from zope.interface import Interface
  >>> from zope.security.checker import defineChecker
  >>> from zope.publisher.browser import TestRequest
  >>> from zope.publisher.interfaces.browser import IBrowserRequest
  >>> from zope.component.interfaces import IView
  >>> from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
  >>> from zope.app.publisher.browser import BrowserView
  >>> from zope.app.pagelet.interfaces import IPagelet
  >>> from zope.app.pagelet.interfaces import IPageletSlot
  >>> from zope.app.pagelet.interfaces import IMacrosCollector
  >>> from zope.app.pagelet.tales import TALESPageletsExpression
  >>> from zope.app.pagelet.collector import MacrosCollector
  >>> from zope.app.pagelet.tests import TestPagelet
  >>> from zope.app.pagelet.tests import TestContext
  >>> from zope.app.pagelet.tests import testChecker

Setup:

  >>> gsm = zapi.getGlobalSiteManager()

Register slot interface:

  >>> from zope.app.component.interface import provideInterface
  >>> provideInterface('', IPageletSlot, None)

Register TALES pagelet expression:

  >>> from zope.app.pagetemplate.metaconfigure import registerType
  >>> registerType('pagelets', TALESPageletsExpression)

Define a pagelet in a ZCML directive pagelet like:

<zope:pagelet
  name="demopagelet"
  layer="zope.publisher.interfaces.browser.IBrowserRequest"
  slot="zope.app.pagelet.interfaces.IPageletSlot"
  template="path_to/pagelet.pt"
  for="*"
  permission="zope.View"
  weight="0"
  />

Setup a test pagelet:

  >>> name = 'testpagelet'
  >>> pagelet_factory = TestPagelet
  >>> defineChecker(pagelet_factory, testChecker)
  >>> gsm.provideAdapter(
  ...        (Interface, IBrowserRequest, IView, IPageletSlot)
  ...        , IPagelet, name, pagelet_factory)

Register pagelet collector as a adapter:

  >>> collector_factory = MacrosCollector
  >>> gsm.provideAdapter(
  ...        (Interface, IBrowserRequest, IView, IPageletSlot)
  ...        , IMacrosCollector, '', collector_factory)

Setup a simply browser view with a 'index_pagelets.pt' template:

  >>> ob = TestContext()
  >>> request = TestRequest()
  >>> view = BrowserView(ob, request)

Setup a view page template called 'index':

  >>> from zope.app.pagelet.tests import testfiles
  >>> import os.path
  >>> path = os.path.dirname(testfiles.__file__)
  >>> index = ViewPageTemplateFile('index_pagelets.pt', path)

Call the 'index' (view) on the browser view instance the sample pagelet
'index_pagelets.pt' calls pagelets registered for the slot
'zope.app.pagelet.interfaces.IPageletSlot'. We registred the
'test_pagelet' for this slot in the TestPagelet class. For more info
take a look at the index_pagelets.pt' file in the tests/testfiles folder:

  >>> html = index(view, request)

Test if the pagelet content is in the html output:

  >>> import string
  >>> string.count(html, 'testpagelet macro content')
  1

Basic View Registrations
========================

This chapter provide a reference to some of the basic view registrations
required to create a skin from scratch.  However it is reccomended to use a
package like `z3c.layer.minimal` for creating a skin from scratch.

zope.formlib
------------

::

  <zope:view
      type="LAYER-INTERFACE"
      for="zope.formlib.interfaces.IWidgetInputError"
      provides="zope.formlib.interfaces.IWidgetInputErrorView"
      factory="zope.formlib.exception.WidgetInputErrorView"
      permission="zope.Public"
      />

zope.security
-------------

::

  <zope:view
      type="LAYER-INTERFACE"
      for="zope.security.interfaces.IUnauthorized"
      name="index.html"
      factory="zope.app.http.exception.unauthorized.Unauthorized"
      permission="zope.Public"
      />

  <zope:view
      type="LAYER-INTERFACE"
      for="zope.publisher.interfaces.ITraversalException"
      name="index.html"
      factory="zope.app.http.exception.notfound.NotFound"
      permission="zope.Public"
      />

zope.app.publication
--------------------

::

  <browser:view
      layer="LAYER-INTERFACE"
      for="zope.app.publication.interfaces.IFileContent"
      provides="zope.publisher.interfaces.browser.IBrowserPublisher"
      class="zope.app.publication.traversers.FileContentTraverser"
      permission="zope.Public"
      />

zope.location
-------------

::

  <browser:page
      layer="LAYER-INTERFACE"
      for="zope.location.interfaces.ISite"
      name=""
      class="zope.app.publisher.browser.resources.Resources"
      allowed_interface="zope.publisher.interfaces.browser.IBrowserPublisher"
      permission="zope.Public"
      />

zope.traversing
---------------

::

  <zope:view
      type="LAYER-INTERFACE"
      for="*"
      name="etc"
      provides="zope.traversing.interfaces.ITraversable"
      factory="zope.traversing.namespace.etc"
      />

  <zope:view
      type="LAYER-INTERFACE"
      for="*"
      name="attribute"
      provides="zope.traversing.interfaces.ITraversable" 
      factory="zope.traversing.namespace.attr"
      />

  <zope:view
      type="LAYER-INTERFACE"
      for="*"
      name="adapter"
      provides="zope.traversing.interfaces.ITraversable" 
      factory="zope.traversing.namespace.adapter"
      />

  <zope:view
      type="LAYER-INTERFACE"
      for="*"
      name="item"
      provides="zope.traversing.interfaces.ITraversable"
      factory="zope.traversing.namespace.item"
      />

  <zope:view
      type="LAYER-INTERFACE"
      for="*"
      name="acquire"
      provides="zope.traversing.interfaces.ITraversable"
      factory="zope.traversing.namespace.acquire"
      />

  <zope:view
      type="LAYER-INTERFACE"
      for="*"
      name="view"
      provides="zope.traversing.interfaces.ITraversable"
      factory="zope.traversing.namespace.view"
      />

  <zope:view
      type="LAYER-INTERFACE"
      for="*"
      name="resource"
      provides="zope.traversing.interfaces.ITraversable"
      factory="zope.traversing.namespace.resource"
      />

  <zope:view
      type="LAYER-INTERFACE"
      for="*"
      name="skin"
      provides="zope.traversing.interfaces.ITraversable"
      factory="zope.traversing.namespace.skin"
      />

  <zope:view
      type="LAYER-INTERFACE"
      for="*"
      name="vh"
      provides="zope.traversing.interfaces.ITraversable"
      factory="zope.traversing.namespace.vh"
      />

  <zope:view
      type="LAYER-INTERFACE"
      for="*"
      name="debug"
      provides="zope.traversing.interfaces.ITraversable"
      factory="zope.traversing.namespace.debug"
      />

zope.traversing.browser
-----------------------

::

  <zope:adapter
      for="zope.interface.Interface
           LAYER-INTERFACE"
      provides="zope.publisher.interfaces.browser.IBrowserPublisher"
      factory="zope.app.publication.traversers.SimpleComponentTraverser"
      permission="zope.Public"
      />

  <zope:adapter
      for="zope.container.interfaces.IItemContainer
           LAYER-INTERFACE"
      provides="zope.publisher.interfaces.browser.IBrowserPublisher"
      factory="zope.container.traversal.ItemTraverser"
      permission="zope.Public"
      />

  <zope:adapter
      for="zope.container.interfaces.ISimpleReadContainer
           LAYER-INTERFACE"
      provides="zope.publisher.interfaces.browser.IBrowserPublisher"
      factory="zope.container.traversal.ItemTraverser"
      permission="zope.Public"
      />

  <zope:view
      type="LAYER-INTERFACE"
      for="*"
      name="absolute_url"
      factory="zope.traversing.browser.AbsoluteURL"
      allowed_interface="zope.traversing.browser.interfaces.IAbsoluteURL"
      permission="zope.Public"
      />

  <zope:view
      type="LAYER-INTERFACE"
      for="*"
      provides="zope.traversing.browser.interfaces.IAbsoluteURL"
      factory="zope.traversing.browser.AbsoluteURL"
      permission="zope.Public"
      />

  <zope:view
      type="LAYER-INTERFACE"
      for="zope.traversing.interfaces.IContainmentRoot"
      name="absolute_url"
      factory="zope.traversing.browser.SiteAbsoluteURL"
      allowed_interface="zope.traversing.browser.interfaces.IAbsoluteURL"
      permission="zope.Public"
      />

  <zope:view
      type="LAYER-INTERFACE"
      for="zope.traversing.interfaces.IContainmentRoot"
      provides="zope.traversing.browser.interfaces.IAbsoluteURL"
      factory="zope.traversing.browser.SiteAbsoluteURL"
      permission="zope.Public"
      />

  <browser:page
      layer="LAYER-INTERFACE"
      for="*"
      name="absolute_url"
      class="zope.traversing.browser.AbsoluteURL"
      allowed_interface="zope.traversing.browser.interfaces.IAbsoluteURL"
      permission="zope.Public"
      />

  <browser:page
      layer="LAYER-INTERFACE"
      for="zope.traversing.interfaces.IContainmentRoot"
      name="absolute_url"
      class="zope.traversing.browser.SiteAbsoluteURL"
      allowed_interface="zope.traversing.browser.interfaces.IAbsoluteURL"
      permission="zope.Public"
      />

browser
-------

::

  <browser:page
      layer="LAYER-INTERFACE"
      for="zope.interface.common.interfaces.IException"
      name="index.html"
      class="zope.app.exception.systemerror.SystemErrorView"
      template="systemerror.pt"
      permission="zope.Public"
      />

  <browser:page
      layer="LAYER-INTERFACE"
      for="zope.publisher.interfaces.ITraversalException"
      name="index.html"
      class="zope.app.exception.systemerror.SystemErrorView"
      template="systemerror.pt"
      permission="zope.Public"
      />

  <browser:page
      layer="LAYER-INTERFACE"
      for="zope.security.interfaces.IUnauthorized"
      name="index.html"
      class="zope.app.exception.browser.unauthorized.Unauthorized"
      template="unauthorized.pt"
      permission="zope.Public"
      />

  <browser:page
      layer="LAYER-INTERFACE"
      for="zope.exceptions.interfaces.IUserError"
      name="index.html"
      class="zope.app.exception.browser.user.UserErrorView"
      template="user.pt"
      permission="zope.Public"
      />

  <browser:page
      layer="LAYER-INTERFACE"
      for="zope.publisher.interfaces.INotFound"
      name="index.html"
      class="zope.app.exception.browser.notfound.NotFound"
      template="notfound.pt"
      permission="zope.Public"
      />

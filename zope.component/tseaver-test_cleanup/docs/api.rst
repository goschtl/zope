:mod:`zope.component` API
=========================


Site Manager APIs
-----------------

.. autofunction:: zope.component.getGlobalSiteManager

   The API returns the module-scope global registry:

   .. doctest::

      >>> from zope.component.interfaces import IComponentLookup
      >>> from zope.component.globalregistry import base
      >>> from zope.component import getGlobalSiteManager
      >>> gsm = getGlobalSiteManager()
      >>> gsm is base
      True

   The registry implements the
   :class:`~zope.component.interfaces.IComponentLookup` interface:

   .. doctest::

      >>> IComponentLookup.providedBy(gsm)
      True

   The same registry is returned each time we call the function:

   .. doctest::

      >>> getGlobalSiteManager() is gsm
      True

.. autofunction:: zope.component.getSiteManager(context=None)

   We don't know anything about the default service manager, except that it
   is an `IComponentLookup`.

   .. doctest::

     >>> from zope.component import getSiteManager
     >>> from zope.component.interfaces import IComponentLookup
     >>> IComponentLookup.providedBy(getSiteManager())
     True

   Calling `getSiteManager()` with no args is equivalent to calling it with a
   context of `None`.

   .. doctest::

     >>> getSiteManager() is getSiteManager(None)
     True

   If the context passed to `getSiteManager()` is not `None`, it is
   adapted to `IComponentLookup` and this adapter returned.  So, we
   create a context that can be adapted to `IComponentLookup` using
   the `__conform__` API.

   Let's create the simplest stub-implementation of a site manager possible:

   .. doctest::

     >>> sitemanager = object()

   Now create a context that knows how to adapt to our newly created site
   manager.

   .. doctest::

     >>> from zope.component.tests.test_doctests \
     ...    import ConformsToIComponentLookup
     >>> context = ConformsToIComponentLookup(sitemanager)

   Now make sure that the `getSiteManager()` API call returns the correct
   site manager.

   .. doctest::

     >>> getSiteManager(context) is sitemanager
     True

   Using a context that is not adaptable to `IComponentLookup` should fail.

   .. doctest::

     >>> getSiteManager(sitemanager)
     Traceback (most recent call last):
     ...
     ComponentLookupError: ('Could not adapt', <instance Ob>,
     <InterfaceClass zope...interfaces.IComponentLookup>)


Utility Registration APIs
-------------------------

Utilities are components that simply provide an interface. They are
instantiated at the time or before they are registered. Here we test the
simple query interface.

Before we register any utility, there is no utility available, of
course. The pure instatiation of an object does not make it a utility. If
you do not specify a default, you get a `ComponentLookupError`.

.. testsetup::

   from zope.component.testing import setUp
   setUp()

.. doctest::

   >>> from zope.component import getUtility
   >>> from zope.component import queryUtility
   >>> from zope.component.tests.test_doctests import I1
   >>> getUtility(I1) #doctest: +NORMALIZE_WHITESPACE
   Traceback (most recent call last):
   ...
   ComponentLookupError: \
   (<InterfaceClass zope.component.tests.test_doctests.I1>, '')

Otherwise, you get the default:

.. doctest::

   >>> queryUtility(I1, default='<default>')
   '<default>'

Now we declare `ob` to be the utility providing `I1`:

.. doctest::

   >>> ob = object()
   >>> from zope.component import getGlobalSiteManager
   >>> getGlobalSiteManager().registerUtility(ob, I1)

Now the component is available:

.. doctest::

   >>> getUtility(I1) is ob
   True
   >>> queryUtility(I1) is ob
   True

Registering a utility without a name does not mean that it is available
when looking for the utility with a name:

.. doctest::

   >>> getUtility(I1, name='foo')
   Traceback (most recent call last):
   ...
   ComponentLookupError:
   (<InterfaceClass zope.component.tests.test_doctests.I1>, 'foo')

   >>> queryUtility(I1, name='foo', default='<default>')
   '<default>'

Registering the utility under the correct name makes it available:

.. doctest::

   >>> getGlobalSiteManager().registerUtility(ob, I1, name='foo')
   >>> getUtility(I1, 'foo') is ob
   True
   >>> queryUtility(I1, 'foo') is ob
   True


.. testcleanup::

   from zope.component.testing import tearDown
   tearDown()


.. autofunction:: zope.component.getUtility

.. autofunction:: zope.component.queryUtility



:mod:`zope.component.interfaces`
================================

.. automodule:: zope.component.interfaces

   .. autointerface:: IComponentArchitecture
      :members:
      :member-order: bysource

   .. autointerface:: IRegistry
      :members:
      :member-order: bysource

   .. autointerface:: IComponentRegistrationConvenience
      :members:
      :member-order: bysource

   .. autointerface:: IPossibleSite
      :members:
      :member-order: bysource

   .. autointerface:: ISite
      :members:
      :member-order: bysource

   .. autoexception:: Misused

   .. autointerface:: IFactory
      :members:
      :member-order: bysource

==============
Local Services
==============

:Author: Jim Fulton
:Version: $Revision: 1.3 $

.. contents::

This package includes implementations of several local services.
It also contains infrastructure for implementing local services.

This document describes how to implement local services.  It's not
too difficult, but there can be a lot of details that are hard to
remember.

A service is a component that implements a specific interface *and*
that has the responsibility to collaborate with services above it.
Local services are stored in the Zope object database, so they also
need to be persistent.  Finally, many local services support modular
configuration through configuration objects.

A few words on the difference between local and global services:

- Local services (usually) exist in the ZODB; global services don't.

- Local services apply to a specific part of the object hierarchy;
  global services (as their name suggests) don't.

- Local services are (usually) created and configured through the ZMI;
  global services are created and configured by ZCML directives.

- Local services are expected to collaborate with services "above"
  them in the object hierarchy, or with the global service; global
  services by definition have nothing "above" them.

Let's walk through an example step by step.  We'll implement a
local utility service.  A utility service must implement the
interface ``zope.component.interfaces.IUtilityService``.


Step 1. Create a minimal service
--------------------------------

Create a minimal service that delagates everything to the
service above it, in the file ``utility.py``::

  from persistence import Persistent
  from zope.component.exceptions import ComponentLookupError
  from zope.proxy.context import ContextAware
  from zope.app.component.nextservice import getNextService
  from zope.component.interfaces import IUtilityService
  from zope.app.interfaces.services.interfaces import ISimpleService

  class LocalUtilityService(Persistent, ContextAware):

      __implements__ = IUtilityService, ISimpleService

      def getUtility(self, interface, name=''):
          utility = self.queryUtility(interface, name=name)
          if utility is None:
              raise ComponentLookupError("utility", interface, name)
          return utility

      def queryUtility(self, interface, default=None, name=''):
          next = getNextService(self, "Utilities")
          return next.queryUtility(interface, default, name)

The local service subclasses two classes:

``Persistent``
  Provides support for transparent persistent in the ZODB.

``ContextAware``
  Causes all of the methods or properties defined in
  the class (or base classes) to be bound to context-wrapped
  instances.  This is needed if the methods or properties are going to
  call APIs that need acquisition context.  We could convert each of
  the methods to context methods individually, but it's easier to just
  mix-in context aware.

The ``getUtility`` method simply delegates to ``queryUtility``.  The
``queryUtility`` method delegates to the next utility service using
``getNextService``.  (Both methods are specified by the
``IUtilityService`` interface.)

The function ``getNextService`` looks up the next service above the
current service.  It takes a location and a service name.  We use it
to get the interface service defined above our service, which may be
the global service, and delegate to it.

I created the service in the ``utility`` module in this package (the
file ``utility.py``).  This package is already pretty large.  To avoid
a really large zcml file, I've started giving each service its own
zcml file.  So I also created an ``utility.zcml`` file::

  <zopeConfigure xmlns="http://namespaces.zope.org/zope">

  <content class=".utility.LocalUtilityService">
    <factory
        id="zope.app.services.UtilityService"
        permission="zope.ManageServices"
        />
  </content>

  </zopeConfigure>

and I added an include to the package configuration file::

  <!-- Utility Service --> <include file="utility.zcml" />

To make it possible to add the utility service, I need to add an entry to
the ``add_component`` browser menu.  The ``add_component`` menu is the menu
used by site folders for adding objects.  To do this, I need to add a
browser menu configuration.  Eventually, the local interface will
have a number of views, so I create a package, ``utility``, for
it in ``zope/app/browser/services``.  [1]_ In that
package, I put a configuration that defines the needed browser menu
item::

   <zopeConfigure xmlns="http://namespaces.zope.org/browser">

   <menuItem
         for="zope.app.interfaces.container.IAdding"
         menu="add_service"
         action="zope.app.services.UtilityService"
         title="Utility Service"
         permission="zope.ManageServices"
         />

   </zopeConfigure>

and I added an include to the configuration file in
zope.app.browser.services::

   <!-- Utility Service --> <include package=".utility" />

With this in place, I can add a local service that does nothing but
delegate to a service above it.  (To actually create a utility service
instance, I have to go to the service manager and use its ``Add
service`` action.  The service manager is reached from the root folder
by using the ``Manage local services`` action.)


Step 2. Providing functionality
-------------------------------

Now it's time to add some functionality.  A utility service keeps
track of utility components by name and interface.  It allows
components to be registered and then looked up later.

An important feature of component registration services, like the
utility service, is that they support multiple conflicting
registrations.  At most one of the registrations is active.  A site
developer can switch between alternate components by simply changing
which one is active.

Consider the following scenario.  A product provides a utility.  A
site manager gets a new version of the utility and installs
it.  The new version is active.  The site developer then finds a
bug in the new version.  Because the old utility is still registered,
the site developer can easily switch back to it by making it active.

Utilities can be provided in two ways:

- As persistent objects in (site-management) folders.

- As module global objects.  (A variation is to point to a class
  that can be called without arguments to create a utility.)

We'd like to avoid making the utility service have to deal with
these variations directly.

We want to make it possible for folders to provide configurations
that can be reused in different sites.

To support the configuration flexibility described above, Zope
provides a configuration framework:

- Configuration registry objects manage multiple configurations for
  the same configuration parameters (at most one of which is active at
  any given time).  For example, in the case of a utility service
  these would be configurations for the same interface and name.

- Configuration objects provide configuration data.

- Configuration managers support management of configuration objects
  in folders.

We'll start by updating the utility service to support configurations.
The updated local utility service implementation can be found in
zope/app/services/utility.py.

First, we'll pick a data structure.  We'll use a persistent dictionary
mapping utility names to implementor registries.  An implementor
registry implements a mapping from interfaces to objects; it's not
quite the same as a mapping because it understands subclassing
relationships between the interfaces used as keys.  In this case, the
implementor registries themselves map interfaces to configuration
registries.

We also need to implement
zope.app.interfaces.services.configuration.IConfigurable.  This
defines two methods, ``queryConfigurationsFor`` and
``createConfigurationsFor``.

A ``queryConfigurationsFor`` method is added to implement
``IConfigurable``.  It takes a configuration object and returns the
corresponding configuration registry.  The configuration object is
used to provide an abstract way to represent configuration parameters.
Typically, the configuration parameters are extracted and a more
concrete method is called.  In the local utility service, we extract
the utility name and interface and call ``queryConfigurations`` with
the name and interface.

Similarly, we add a ``createConfigurationsFor`` method that takes a
configuration object holding configuration parameters and creates a
configuration registry for the parameters (if none already exists).
If we don't have a implementor registry for a utility name, we create
one and add it.  When we create the implementor registry, we pass a
``PersistentDict`` for it to use to store registration data.  This
assures that updates are made persistently.  If there isn't implementor
data for the given interface, we create a configuration registry and
register it for the interface.

Finally, we modify ``queryUtility`` to use registered utility
configurations.  We try to get a configuration registery by calling
``queryConfigurations``.  If we get one, we call its ``active``
method to get the active configuration, if any.  Finally, we call
``getComponent`` on the active configuration to get the actual
component.  We leave it up to the configuration object to take care of
actually finding and returning the component.

Our local utility service is now complete, except for a user
interface.  We need to provide utility configuration objects.  The
utility configuration objects need to manage several bits of
information:

- name

- interface

- permission

- The location of the actual component.

We'll start by creating a configuration class for utility components
stored in folders.  Somewhat different approaches are taken for
configuring components contained in folders and objects contained in
modules.  Objects contained in folders provide a configurations view
that shows the configurations for the object and lets you add
configurations.  When we add these objects, we typically add
configurations at the same time.

To create the configuration class, we'll start by defining a
configuration schema in
``zope/app/interfaces/services/utility.py``.  The schema should extend
``zope.app.interfaces.services.configuration.IConfiguration``.
There's a more specific interface,
``zope.app.interfaces.services.configuration.IComponentConfiguration``
that is much closer to what we need.  (XXX Add footnote explaining why
we can't use INamedComponentConfiguration in this example.)
We extend this interface as IUtilityConfiguration, which adds a name
field (which is required but may be empty -- note the subtle
difference, because the empty string is still used as part of the
lookup key) and an interface field.  We also override the
componentPath field to make it read-only (this is for the UI
definition).

A ``UtilityConfiguration`` class is added to the ``utility`` module in
``zope/app/services`` that implements the configuration interface.
We can subclass ComponentConfiguration, which does much of the work.


For utility components stored in folders, we want to do the
configuration through the components themselves.  That is, the site
admin should be able to walk up to a component that implements a
utility and add or change a utility configuration for it.  The most
common case is actually that a site manager creates a utility
component and configures it right away.  (This is the same common case
that is used for creating and configuring services.)

There's a view on utility components for managing their
configurations; similar to the corresponding view on service
components, it shows a list of all configurations for the component,
and a link to add a new one.

To implement this view, we need to keep track of the
configuration objects for given utility components.  The reference
from a configuration object to the component it configures is
contained in the configuration object itself.  In order to find the
configurations pertaining to a component, we have to implement back
pointers somehow.  Requiring each component to keep track of these
back pointers would be impractical; fortunately there's a general
mechanism that we can use.

The general mechanism is called "annotations".  See
zope/app/interfaces/annotation.py for the full scoop.  The short
version: by adapting an object to IAnnotations, we get a mapping-like
interface that allows us to store arbitrary named data for the object.
In the most common implemenation variant (see
zope/app/attributeannotations.py), all annotation data is stored in a
dictionary which itself is stored as the attribute __annotations__.
Because we don't want to stomp on a component's attributes (even if
they have a __funky__ name) without its permission, a component must
declare that it implements IAttributeAnnotatable; the implementation
is registered as an adapter from this interface to IAnnotations.

To store the configuration back pointers on components, we use an
annotation named "zope.app.services.configuration.UseConfiguration".
(By convention, annotation keys should contain the full dotted name of
the module or class that uses them.)  By adapting a component to
IUseConfiguration, we get an interface defining methods ``addUsage``,
``removeUsage`` and ``usages``, which provide access to the back
pointers.

We also need to provide two summary lines for the configuration
manager.  These summary lines are returned by two methods that are
(questionably, but conveniently) defined in the IConfiguration
interface: usageSummary() and implementationSummary().  We override
usageSummary() to return a string of the form "<interface> utility
[named <name>]"; we inherit implementationSummary() from the
ComponentConfiguration base class, which returns the component
pathname as a string.  These two lines are used in the configuration
manager's default view, which lists all the configurations it knows
about; the first line is a a link to an edit view for configuration
object.

We're now ready to write view code.  We will create three views:

- A "Configurations" view for utility components.

- An "add configuration" view to configure a utility.

- An "edit configuration" view to change a utility's configuration.


The first view we create is the "Configurations" view for utility
components.  This is very similar to the Configurations view for
service components, and for several other components that are handled
by the configuration manager.  The view is a "tab" on any object that
implements ILocalUtility; the view name is useConfigurations.html and
the tab label is "Configurations".  All this is expressed by the ZCML
for the view, in zope/app/browser/services/utility/configure.zcml::

  <page
      for="zope.app.interfaces.services.utility.ILocalUtility"
      name="useConfiguration.html"
      template="useconfiguration.pt"
      class=".useconfiguration.UseConfiguration"
      permission="zope.ManageServices"
      menu="zmi_views" title="Configurations"
      />

We won't show the template (useconfiguration.pt) here; it renders a
bulleted list giving links to the configurations (each linking to the
edit view for the configuration object), and a link to add a new
configuration.

The information for the bulleted list is computed by the
UseConfiguration class in the file useconfiguration.py, which we also
won't show here.  As described earlier, it adapts the component to
IUseConfiguration and gets the back pointers to configuration objects
from the adapter's usages() method.  For each configuration object it
returns enough information to render the utility's interface, name,
activity status, and URL.


The second view we create is the add view for utility configurations.
Here's the ZCML::

  <addform
      for="zope.app.interfaces.services.utility.ILocalUtility"
      name="addConfiguration.html"
      schema="zope.app.interfaces.services.utility.IUtilityConfiguration"
      class=".useconfiguration.AddConfiguration"
      permission="zope.ManageServices"
      content_factory="zope.app.services.utility.UtilityConfiguration"
      arguments="name interface componentPath"
      set_after_add="status"
      fields="name interface componentPath permission status"
      />

(XXX Maybe briefly explain each attribute, like we do below for
<editform>?)

Notice that there's no template!  The <addform> directive creates the
form for us using a generic template, zope/app/browser/form/add.pt,
and information about the specific fields to be displayed extracted
from the schema.  We do specify a class name: the AddConfiguration
class.  This class needs some explanation.

The ``for=`` attribute says that this view applies to all objects that
implement the ILocalUtility interface.  All utility components should
implement this interface in order to be configurable as a utility.
This interface extends IUseConfigurable, which is required so that a
utility component can keep track of the back pointers to configuration
objects that reference it, as was discussed above.  Utility components
should also implement IAttributeAnnotatable, unless they want to
provide a different way to store annotations.

The <addform> directive uses the AddConfiguration class as a mix-in
class.  It may override various methods to customize the add form; the
set of methods that can be customized is given by the
``zope.app.interfaces.browser.form.IAddFormCustomization class``.  In this
particular case, we must override ``add`` and ``nextURL`` because their
default implementations only work when the add form is a view on an
IAdding view.  That is the normal way to use add forms, but here we
don't do that; this particular add form is a view on a local utility
component.  Our ``AddConfiguration`` class subclasses
``zope.app.browser.services.configuration.AddComponentConfiguration``,
which provides the implementations of ``add`` and ``nextURL`` that we
need. The ``add`` method defined in ``AddComponentConfiguration``
finds the congiguration manager in the current folder and adds the new
configuration object to it.


The AddConfiguration class defines a class attribute::

    interface = CustomWidget(UtilityInterfaceWidget)

This tells the forms machinery to use a a custom widget for the
interface field. The custom widget we use is a specialized interface
widget that allows the user to select from the non-trivial interfaces
implemented by the component being configured.

The third view we create is the edit view for utility configuration
objects.  This view looks similar to the add view, but its definition
is simpler, because it isn't deviating quite as much from a standard
edit view::

  <editform
      name="index.html"
      menu="zmi_views" title="Edit"
      schema="zope.app.interfaces.services.utility.IUtilityConfiguration"
      label="Utility Configuration"
      permission="zope.ManageServices"
      fields="name interface componentPath permission status"
      />

This is a view on IUtilityConfiguration, which is typical for an edit
view.  The good news is that it has no template *or* class!  The
<editform> directive lets us specifiy all the customization we need:

- ``name=``: The view name.  This is the last component of the URL for
  the view.

- ``menu=``, ``title=``: Menu information: "zmi_views" means that this
  view is one of the "tabs" for this type of object, the title
  argument gives the text in the tab.

- ``schema=``: The interface used as the schema.  The field
  definitions in this interface define which attributes are displayed
  in the form, and how.

- ``label=``: The label, used as the title text in the view.

- ``permission=``: A permission needed to access the view.

- ``fields=``: A list of fields to be displayed in the form.  This is
  used here to force the order in which the fields are displayed.  It
  can also be used to display only a subset of the fields present in
  the schema.

And that's all there is to the edit view.  Some observable differences
between the edit view and the add view:

- The add view lets you specify the name or the interface; the edit
  view displays these fields read-only.

- When you submit the add view, you are redirected to the
  configuration manager; the edit view takes you back to itself.



To do:

  Describe the demo utility

  Need a UI for browsing registered utilities in the utility service.

  Configuration of module globals

    - Need the configuration object class that keeps track of:

      o name

      o interface

      o dotted name

      o permission

    - Add view for the configuration

    - Edit view for the configuration

    - Summary view of the configuration in a configuration registry

    - Summary view of the configuration in a configuration manager











---------------------------------------------------------------

.. [1] Of course, I initially forgot to include a nearly empty
   ``__init__.py`` file and had to add one later.

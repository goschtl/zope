====================
ZAM Plugin Framework
====================

The plugin framework allows us to write "3rd party" software that depends on
the base system's API, but the base system does not in any way depend on the
new software. This allows us to keep the base system compact, and separate
optional features into clearly separated packages.

There are two different type of plugins offered. A simple plugin can do what it
needs to do during the install and unistall process. The other base registry
supported plugin will install a custom component registry.

The fundamental concept of the package is that a plugin can be installed for a
particular site. At any time, you can ask the plugin, whether it has been
installed for a particular site. The third API method allows you to uninstall
the plugin from a site.

So let's implement a trivial plugin that stores an attribute:

  >>> from zam.api import plugin

  >>> class SamplePlugin(plugin.Plugin):
  ...     title = u'Sample'
  ...     description = u'Sample Attribute Plugin'
  ...
  ...     def isInstalled(self, site):
  ...         """See interfaces.IPlugin"""
  ...         return hasattr(site, 'sample')
  ...
  ...     def install(self, site):
  ...         """See interfaces.IPlugin"""
  ...         if not self.isInstalled(site):
  ...             setattr(site, 'sample', 1)
  ...
  ...     def uninstall(self, site):
  ...         """See interfaces.IPlugin"""
  ...         if self.isInstalled(site):
  ...             delattr(site, 'sample')

The title and description of the plugin serve as pieces of information for the
user and are commonly used in the UI.

So let's use the sample plugin:

  >>> from zam.api import testing
  >>> site = testing.ZAMTestSite(u'ZAM Test Site')
  >>> sm = site.getSiteManager()

  >>> sample = SamplePlugin()

At the beginning the plugin is not installed, so we that first:

  >>> sample.isInstalled(site)
  False

  >>> sample.install(site)
  >>> site.sample
  1

  >>> sample.isInstalled(site)
  True

However, once the plugin is isntalled, it cannot be installed again:

  >>> site.sample = 2

  >>> sample.install(site)
  >>> site.sample
  2

This is a requirement of the API. Now you can also uninstall the plugin:

  >>> sample.uninstall(site)
  >>> sample.isInstalled(site)
  False
  >>> site.sample
  Traceback (most recent call last):
  ...
  AttributeError: 'ZAMTestSite' object has no attribute 'sample'

You cannot uninstall the plugin again:

  >>> sample.uninstall(site)


Base Registry Plugins
---------------------

An important base implementation is a plugin that installs a new base registry
to the to the site.

We also need a base registry for the plugin:

  >>> import zope.component
  >>> from z3c.baseregistry import baseregistry

  >>> sampleRegistry = baseregistry.BaseComponents(
  ...     zope.component.globalSiteManager, 'sampleRegistry')

Now we can create the plugin, either through instantiation or subsclassing:

  >>> class SampleRegistryPlugin(plugin.BaseRegistryPlugin):
  ...     title = u'Sample Registry'
  ...     description = u'Sample Registry Plugin'
  ...     registry = sampleRegistry

  >>> regPlugin = SampleRegistryPlugin()

We use the same API methods as before. Initially the plugin is not installed:

  >>> sampleRegistry in sm.__bases__
  False
  >>> regPlugin.isInstalled(site)
  False

Now we install the plugin:

  >>> regPlugin.install(site)

  >>> sampleRegistry in sm.__bases__
  True
  >>> regPlugin.isInstalled(site)
  True

As before installing the plugin again does nothing:

  >>> len(sm.__bases__)
  2

  >>> regPlugin.install(site)

  >>> len(sm.__bases__)
  2

And uninstalling the plugin is equally simple:

  >>> regPlugin.uninstall(site)

  >>> sampleRegistry in sm.__bases__
  False
  >>> regPlugin.isInstalled(site)
  False
  >>> len(sm.__bases__)
  1

Uninstalling a second time does nothing:

  >>> regPlugin.uninstall(site)

  >>> sampleRegistry in sm.__bases__
  False
  >>> len(sm.__bases__)
  1


Layers
------

We offer a fine grained layer concept which allows you to use the ZAM skin
out of the box or you can define your own skins offering what you need.
Each ZAM plugin should configure it's component for the IZAMBrwoserLayer and
not for the IZAMCoreLayer. This allows others to use the IZAMCoreLayer without
any plugin configuration. See the different layer descriptions below for more
information about the ZAM layer concept.


Big note
~~~~~~~~

This is only important if you'd like to define a own skin which uses
selective zam plugins.

The layer concept has some limitations if it comes to the adapter lookup. It's
not possible to define a custom layer and make an existing layer act like it
whould inherit this layer. Implements and provide concept only work on classes
but not on interfaces. Let's be correct, they work but doesn't affect the
request. Which means the request doesn't know about such applied layers. This
means there is no[*] way to apply a later defined layer to an existing layer.
This is the reason why we offer all plugin layers in the zam.api.layer package.
But what does this mean if you'd like to define custom plugins and their layers?
You have to define your own skin and inherit your new layers in this skin.
You can skip the named skin configuration and configure your custom skin.

[*] Ok, there is a way to apply layers to an existing layer or at least it will
do the same effect. There are two ways, you can add a SkinChangedEvent which
will do an alsoProvide and inject your layer or you can use a before traversal
event subscriber which does the same. I decided not to use these patterns here
as default because such subscriber will affect every skin and will cost
processing time on every request. The option we have with defining an explicit
configuration for a custom skin is to small to pay that price.


IZAMCoreLayer
~~~~~~~~~~~~~

The core layer provides the ZAM core management views but no plugins and
skin configuration. This allows us to write skins with a selective choice
of plugins. Of course each plugin must be configured again for your
custom skin. There is no way to offer out of the box a working set without
to configure a plugin twice using two different layers.


IZAMPluginLayer
~~~~~~~~~~~~~~~

The zam plugin layer should not be used in plugins. You need to define a
plugin layer for your plugin in zam.api.layer and use this new defined layer.
This layer will then become a part of the IZAMPluginLayer. This makes it
possible to use the IZAMPluginLayer and get all it's configuration.

But what happens if you don't develop in the zamplugin.* namespace? Then you
only have the option to configure your plugins for an additional layer and use
another skin which uses the IZAMPluginLayer and your custom layer. Using the
IAZMPluginLayer for your configuration and sharing such packages ends in
bad configuration and others needs to exlude your configuration and if this
is not needed in every skin they provide and is based on IZAMPluginLayer.
Of course you can do this in your own private projects, but please do not
use it for public shared packages and help us to provide a clean
IZAMPluginLayer.

Any improvement which offers us a better layer usage concept is very welcome if
it doesn't need to configure additional subscribers.


IZAMBrowserLayer
~~~~~~~~~~~~~~~~

This is the "all in one" layer which can be used for build skins which knows
about all plugin configurations. All plugins should use this layer.


IZAMSkinLayer
~~~~~~~~~~~~~

The IZAMSkinLayer offers the UI part for ZAM but is not registered as skin.
You can use this layer as base if you'd like to develop a custom skin. This
layer contains the nested div menu implementation.


IZAMBrowserSkin
~~~~~~~~~~~~~~~

The IZAMBrowserSkin uses the IZAMSkinLayer and IZAMBrowserLayer and offers the
UI part for ZAM as named skin. This means the IZAMBrowserSkin is accessible
as ++skin++ZAM.

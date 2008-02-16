====================
ZAM Plugin Framework
====================

The plugin framework allows us to write "3rd party" software that depends on
the base system's API, but the base system does not in any way depend on the
new software. This allows us to keep the base system compact, and separate
optional features into clearly separated packages.

There are two different type of plugins offered. A simple plugin can do what it
needs to do during the install and unistall process. The other base registry
supported plugin will install a customcomponent registry.

The fundamental concept of the package is that a plugin can be installed for a
particular site. At any time, you can ask the plugin, whether it has been
installed for a prticular site. The third API method allows you to uninstall
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

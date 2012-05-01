=================
grokcore.resource
=================

`grokcore.resource` is a package destined to integrate `fanstatic`
into Grok applications.


Including resources in components
=================================

When rendering a web page we want to be able to include the resources
where we need them.

There are several ways to include them. It can be done automatically
upon traversal on any IResourcesIncluder component, or manually specified.

Traversal inclusion
-------------------

For this example, we'll create a view and use the automatic inclusion,
using the `include` directive::

XXX

For the resources to be automatically included during the traversal,
we need to inform the publishing machinery that our component (the
view), is a IResourcesIncluder. This is done automatically, when using
the "include" directive::

XXX

The `include` directive can be stacked, if several resources are to be
included::

XXX

grok.View()
    grokcore.resource.include(a, b, c)

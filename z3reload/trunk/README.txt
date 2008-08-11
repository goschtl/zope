z3reload
========

Version 0.1

http://gintas.pov.lt/z3reload


z3reload is a Zope 3 product that enables automatic reloading of view code.

Make sure to read the *pitfalls* section before you delve in.

View instances are short-lived and references to them are stored very
infrequently, which makes them a good candidate for dynamic reloading.
In addition they are frequently the largest and most complex part of
the code in a typical web application.  Even within the restrictions of
this implementation automatic code reloading is very handy to have as Zope 3
can take a while to restart.

Code of z3reload now resides at the Zope 3 Base (http://codespeak.net/z3).
Use the following command to grab the latest trunk using Subversion:

  svn checkout http://codespeak.net/svn/z3/z3reload/trunk z3reload


Installation
------------

Copy the z3reload directory where Zope 3 can find it, copy all files in
the package-includes/ subdirectory to package-includes/ in Zope 3.


Configuration
-------------

In package-includes/z3reload-configure.zcml (the global one which you created,
not the one inside the package), the namespace `reload` should be registered,
like this:

<configure xmlns="http://namespaces.zope.org/zope"
           xmlns:reload="http://namespaces.pov.lt/z3reload">

In the same file you can specify individual classes, modules or packages which
contain views that should be made reloadable using the ZCML directive
`reload`.  Here is an example:

<reload:reload
    classes="somepackage.somemodule.SomeView
             somepackage.anothermodule.AnotherView"
    modules="anotherpackage.views"
    packages="thirdpackage.browser"
    />

This configuration would make views SomeView and AnotherView reloadable.
All views directly in anotherpackage.views, for example,
anotherpackage.views.FooView (but not anotherpackage.views.admin.BarView),
would be included too.  Finally, all views in all modules that reside
in thirdpackage.browser would be processed (thirdpackage.browser.XView,
thirdpackage.browser.admin.YView, etc.).


Usage
-----

Use the views as you normally would.  The view code will be automatically
reloaded before just before rendering the view each time.


Pitfalls
--------

Only the module that the view code resides in will be reloaded.  E.g., if
you have a view mypackage.browser.admin.AdminView that inherits from
mypackage.browser.ViewBase, the mypackage.browser module will not be
reloaded, and therefore changes in ViewBase will not take effect.

It is important to understand the implications of reloading a Python
module.  Basically, all objects -- classes, functions and others --
defined in the top level of the module "change".  Old references
(frequently in the form of imports) from other modules, however, will
still point to the old objects.  This way you can end up with two
different references to distinct versions of the same class, which may
cause unexpected behaviour with issubclass().  A similar problem can arise
if the module defines interfaces which other modules use.

z3reload can deal with updated views, but it will not notice changes in
other components: adapters, utilities, subscribers.  It will work with
code outside the components (top-level functions and classes other than
the registered one) though.  This is because Zope 3 stores references to
the components at startup time.  It should be possible to reload these
components automatically too, but that would probably require a different
approach, because we would not be able not use the mixin hack.

In general it is a good idea to only use automatic reloading for
non-structural changes such as defining or modifying methods of views
and do an old-fashioned server restart when you make a more significant
change.


Implementation details
----------------------

z3reload waits for the DatabaseOpened event, when all view registration has
been completed, and then walks through the global adapter registry.  For
each view to be processed according to the `reload` directive it installs
the mixin Reloader.

Actually, Zope 3 ZCML directives that register views do not register the
plain view class as a multi-adapter.  Instead, they dynamically construct
a new type which inherits from the given class and from a `simple view` class
(that would be zope.app.pagetemplate.simpleviewclass.simple for views that
have page templates defined in ZCML, and
zope.app.publisher.browser.viewmeta.simple for views that don't).  We use
this fact and add Reloader as the first base class.

Reloader overrides the __init__() method of the real view.  In this method
the module of the class is reloaded and the attribute __bases__ of the class
is updated with a new reference to the reloaded class.  Then __init__ of the
actual reloaded view is invoked.


Gintautas Miliauskas <gintas@pov.lt>
2005-08-20

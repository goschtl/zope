Zope Project Packages

The zope package is a pure namespace package holding packages developed as
part of the Zope 3 project.

Generally, the immediate subpackages of the zope package should be
useful and usable outside of the Zope application server.  Subpackages
of the zope package should have minimal interdependencies, although
most depend on zope.interfaces.

The one package that's not usable outside the application server is
that app package, which *is* the application server. Sub-packages of
app are not usable outside of the application server. If there's
something in app you want to use elsewhere, let us know and we can
talk about abstracting some of it up put of app.


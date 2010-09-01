The ``zope.app.pagetemplate`` package integrates the Page Template
templating system (``zope.pagetemplate``) into the Zope 3 application
server.  In particular, it provides:

* a TALES engine implementation that uses Zope's security system for
  checking access,

* TALES namespace adapters for easy access to DublinCore metadata
  (e.g. ``obj/zope:title``) and URL quoting
  (e.g. ``obj/@@absolute_url/url:quote``).


z3c.themehook Package Readme
============================

Overview
--------
This package contains a publication object that provides a hook for callObject,
so that the calling gets pluggable. The main reason for this is to apply
theming, which is why the module is called "themehook".

Usage
-----
A themehook is a multiadapter between (None, IBrowserRequest) and
z3c.themehook.interfaces.IPublicationObjectCaller. An example can be found
in z3c.themehook.publication.DefaultPublicationObjectCaller which simply
does what Zope 3s default publication object does.

All you need to do to use the themehook is to create a new such adapter
and register it, and it will be automatically used for the whole application.

Wrapper
=======

This is an implementation of the "Basic Context Wrapper" for Zope 3.
More design information and documentation is available at

http://dev.zope.org/Wikis/DevSite/Projects/ComponentArchitecture/BasicContextWrapper

This code requires Python 2.2.

Decorator
=========

A decorator is a subtype of a context wrapper that can forward some messages
to either a fixed set of attributes held in a dict, or to a lazily-created
"mixin" object.
We call the "decorating mixin" object a "mixin" because decoration is a lot
like dynamically subclassing an object's class.


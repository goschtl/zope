********************************************
Zope Packaging of the Ext Javascript library
********************************************

This distribution provides a packaging of the Ext Javascript library,
http://extjs.com/ as a Python package.  It provides both a Zope 3
resource directory named "extjs" and a zc.resourcelibrary resource
library named "Ext".  

This distribution can be used with non-Zope applications, by simply
loading the Ext Javascript and CSS files as package data from the
extjs subdirectory of the zc.extjsresource Python package.

When this distribution is installed, the Ext distribution is
downloaded and included in the installed Python package. (This means
that network access is required to install this package from source.)

To use in Zope 3, include the zc.extjsresource package in your ZCML
and use one of the following resource libraries:

Ext
   To use Ext alone with it's own internal base library

Ext-YUI
   To use Ext built on the Yahoo User Interface library

Ext-jQuery
   To use Ext built on the jQuery library.

Ext-Prototype
   To use Ext built on the Prototype and Scriptaculous libraries.

In Zope 3, if development mode is enabled ("devmode on" in zope.conf),
then unpacked versions of the Ext libraries are used.  These are
larger but make debugging much easoer.


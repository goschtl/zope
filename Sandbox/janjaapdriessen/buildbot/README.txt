Zope buildbot
=============

At the moment of writing the buildbot is running the tests of:

 - zopetoolkit trunk
 - zope2 trunk
 - zope2.12
 - grok trunk
 - groktoolkit trunk
 - lots of grok packages

Supported python versions are 2.4, 2.5, 2.6 and 2.7.

Test slaves win, osx and 32 and 64 bit linux are supported.

Setting up windows build slaves
-------------------------------

We tried to use the collective.buildbot:slave buildout recipe, but to no avail.
Setting up the windows build slaves is a manual process described here:

 - install python 2.4 until 2.7
 - install pywin32 for each of these pythons
 - inside a virtualenv, install zope.interface, twisted and buildbot
 - buildbot create-slave ...

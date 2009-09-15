Zope buildbot
=============

At the moment of writing the buildbot is running the tests of:

 - zopetoolkit trunk
 - zc.buildout trunk
 - grok trunk

Supported python versions are 2.4, 2.5 and 2.6.

Test slaves win, osx and 32 and 64 bit linux are supported.

Setting up windows build slaves
-------------------------------

Build slaves for python versions 2.4, 2.5 and 2.6 are currently supported.

We tried to use the collective.buildbot:slave buildout recipe, but to no avail.
Setting up the windows build slaves is a manual process described here:
  
  http://buildbot.net/trac/wiki/RunningBuildbotOnWindows

Setting up OSX build slaves
---------------------------

See http://buildbot.net/trac/wiki/UsingLaunchd for running stable OSX build
slaves.

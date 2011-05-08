zopeorg.buildout
================

Buildout for the new zope.org website based on Plone 4.
A ZEO server with two clients (instance and client1) are created.

How to install the development version
--------------------------------------

* Have Python 2.6 installed, install virtualenv if not done already and
create a Python environment
$ easy_install virtualenv
$ mkdir zope.org
$ cd zope.org
$ virtualenv --no-site-packages python26

* Get this buildout package via git like so:
$ git clone git://github.com/d2m/zopeorg.buildout.git
$ cd zopeorg.buildout

* Bootstrap buildout and run it with dev.cfg
$ ../python26/bin/python bootstrap.py -d
$ ./bin/buildout -c dev.cfg

* Fire up Zeo and Zope
$ ./bin/zeoserver start
$ ./bin/instance start

* Point your webbrowser to http://localhost:8080 (username admin,
  password admin)
* Create the ZODB mount point in zope's root
http://localhost:8080/manage_addProduct/ZODBMountPoint/addMountsForm
* Install a Plone instance in that mount point (named zopeorg)
http://localhost:8080/manage_addProduct/CMFPlone/zmi_constructor


That's all


Product dependencies from old zope2.zope.org
============================================
Products.TextIndexNG3
Products.PloneFormGen
Products.CacheSetup
Products.PloneArticle
collective.editskinswitcher
collective.portlet.feedmixer==1.3
collective.easyslider
collective.portletpage


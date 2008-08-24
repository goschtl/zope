Grok-by-Example: Wiki
=====================

:Author: d2m (michael at d2m.at)
:Motivation: look at the original source and the Grok code side-by-side 
             and deduce from both

A basic 'Grok Wiki' application [source__] ported from a 
Google Appengine [GAE] example application [source__].

__ http://svn.zope.org/grokapps/gbewiki/src/gbewiki/
__ http://code.google.com/p/google-app-engine-samples/source/browse/trunk/cccwiki/wiki.py


Overview
========

A simple Grok wiki application.

Editing is in a WYSIWYG editor (TinyMCE) rather than a text editor with special
syntax. Users need to create an account and authenticate to edit pages. 
WikiName linking and auto-linking to plain text URLs is supported.


Usage
-----

This example is a complete Grok app on its own. Here is how to use it::

	# checkout the example to your harddisk
	svn co svn://svn.zope.org/repos/main/grokapps/gbewiki
	
	# change to the newly created directory
	cd gbewiki
	
	# make it a virtualenv 
	virtualenv --no-site-packages .
	
	# activate the virtualenv
	source bin/activate
	
	# bootstrap the buildout environment
	bin/python bootstrap.py
	
	# run the buildout
	bin/buildout
	
	# test the example app
	bin/test
	
	# run the example app
	bin/zopectl fg
	
	# point your browser to
	http://localhost:8080
	
	# login
	username: grok
	password: grok
	
	# create an instance of the registered grok app
	# and use it	
	
That's it!

Need help? There is the Grok Users mailinglist at grok-dev@zope.org
(http://mail.zope.org/mailman/listinfo/grok-dev), 
the Grok IRC channel at irc.freenode.net/#grok
and the Grok website at http://grok.zope.org


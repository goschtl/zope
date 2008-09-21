Grok-by-Example: Pastebin
=========================

:Author: d2m (michael at d2m.at)
:Motivation: look at the original source and the Grok code side-by-side 
             and deduce from both

A basic 'Grok Pastebin' application [source__] ported from repoze.cluegun 
[source__], a port of ClueBin__.

__ http://svn.zope.org/grokapps/gbepastebin/src/gbepastebin/
__ http://repoze.org/viewcvs/repoze.cluegun/trunk/
__ http://pypi.python.org/pypi/ClueBin



Overview
========

This is a simple Grok__ Pastebin application.

Allows you to add, view and delete Pastes through a web form. 
Pastes are formatted by the Pygments__ syntax highlighter.

Can also be used as a RESTful service with JSON as response format.
See the functional test file 'app.txt' for details.

__ http://grok.zope.org
__ http://pypi.python.org/pypi/Pygments

Usage
-----

This example is a complete Grok app on its own. Here is how to use it::

	# checkout the example to your harddisk
	svn co svn://svn.zope.org/repos/main/grokapps/gbepastebin
	
	# change to the newly created directory
	cd gbepastebin
	
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


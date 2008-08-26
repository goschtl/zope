Grok-by-Example: Guestbook
==========================

:Author: d2m (michael@d2m.at)
:Motivation: look at the original source and the Grok code side-by-side 
             and deduce from both

A basic 'Grok Guestbook' application [source__] ported from the 
Google Appengine [GAE] demo application [source__].

__ http://svn.zope.org/grokapps/gbeguestbook/src/gbeguestbook/app.py?view=markup
__ http://code.google.com/p/googleappengine/source/browse/trunk/demos/guestbook/guestbook.py


Overview
--------

The application presents you a list of 10 guestbook entries both by 
authenticated and anonymous users, reverse sorted by date of creation
and a form to submit new entries to the guestbook. Response text 
formatting is done using python string templates only.

Usage
-----

This example is a complete Grok app on its own. Here is how to use it::

	# checkout the example to your harddisk
	svn co svn://svn.zope.org/repos/main/grokapps/gbeguestbook
	
	# change to the newly created directory
	cd gbeguestbook
	
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


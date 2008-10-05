Grok-by-Example: 99 Bottles Song
================================

:Author: d2m (michael@d2m.at)
:Motivation: look at the original source and the Grok code side-by-side 
             and deduce from both

A basic Grok 'Hello world' application [source__], cf implementations in other
languages at the '99 Bottles of Beer' website, eg. the Python version [source__].

__ http://svn.zope.org/grokapps/gbe99bottles/src/gbe99bottles/app.py?view=markup
__ http://99-bottles-of-beer.net/language-python-808.html


Overview
========

The '99 Bottles of Beer' website holds a collection of the Song 99 Bottles of 
Beer programmed in different programming languages. Actually the song is 
represented in more than 1200 different programming languages and variations.

The Grok implementation uses persistent 'Wall' and 'Bottle' objects. It follows
the song lyrics by putting bottles on the wall, taking them off again and - at
each step - reporting the state of the scenery.

Usage
-----

This example is a complete Grok app on its own. Here is how to use it::

	# checkout the example to your harddisk
	svn co svn://svn.zope.org/repos/main/grokapps/gbe99bottles
	
	# change to the newly created directory
	cd gbe99bottles
	
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


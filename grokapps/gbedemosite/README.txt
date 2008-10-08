Grok-by-Example: Demosite
=========================

:Author: d2m (michael@d2m.at)


Overview
========

This demosite shows how to install multiple Grok applications and make
them available from a single Grok instance.


Usage
-----

This example is a complete Grok app on its own. Here is how to use it::

	# checkout the example to your harddisk
	svn co svn://svn.zope.org/repos/main/grokapps/gbedemosite
	
	# change to the newly created directory
	cd gbedemosite
	
	# make it a virtualenv 
	virtualenv --no-site-packages .
	
	# activate the virtualenv
	source bin/activate
	
	# checkout a working copy of the different GBE apps
	svn co svn://svn.zope.org/repos/main/grokapps/gbeguestbook
	svn co svn://svn.zope.org/repos/main/grokapps/gbe99bottles
	svn co svn://svn.zope.org/repos/main/grokapps/gbewiki
	svn co svn://svn.zope.org/repos/main/grokapps/gbepastebin
	
	# bootstrap the buildout environment
	bin/python bootstrap.py
	
	# run the buildout
	bin/buildout
	
	# test the example app
	bin/test
	
    # start the ZEO server
    bin/server start
    
    # run the first ZEO client
    bin/zopectl fg
	
	# point your browser to
	http://localhost:8080
	
	# login
	username: grok
	password: grok
	
	# create an instance of the 'Demosite' application
	# (this installs all other GBE apps at once)
	# and use it	
	
	# run the second ZEO client to debug the application
	bin/instance2 debug
	>>> root = app.root()
	>>> list(root.keys())
	...
	# commit your changes back to the ZODB
	>>> import transaction
	>>> transaction.commit()

	
That's it!

Need help? There is the Grok Users mailinglist at grok-dev@zope.org
(http://mail.zope.org/mailman/listinfo/grok-dev), 
the Grok IRC channel at irc.freenode.net/#grok
and the Grok website at http://grok.zope.org


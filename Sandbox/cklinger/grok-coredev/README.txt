============
grokcore-dev
============

Please Note: For this first prototype i used not the trunk of martian
and grokcore.security because these packages don´t work nicely together
with the trunk of the other packgages.

This buildout generates a "out of the box" development
buildout for these grok packages:

- grok
- grokcore.component
- grokcore.view
- grokcore.viewlet
- grokcore.security
- grokcore.formlib
- grokui.admin
- martian

This means that you find in the src directory the fresh checkout´s
of the trunk from the above packages.


mr.developer
------------

The checkout´s are done with help of the buildout.recipe 
mr.developer. For further information please look at the 
pypi package of this package [1] or call the 'bin/develop help'
command which is created during buildout process, and should
show you some further information.

commands
--------

Starting the Grok instance with the wiki-application:

  ./bin/zopectl fg

You can use the debug prompt with:

  ./bin/zopectl debug

You can run the tests for a special package with:  

  ./bin/test -s grokcore.formlib

If you want to run all tests you can run this command

  ./bin/zopepy alltests.py


The ideas for this buildout is from the plone-coredev buildout [2].
So thanks for this...


  
[1] http://pypi.python.org/pypi/mr.developer/0.11
[2] http://dev.plone.org/plone/browser/buildouts/plone-coredev/trunk/

============
grokcore-dev
============

This buildout generates you a "out of the box" development
package for these grok packages:

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

The checkout´s are done with help of the python package 
mr.developer. For further information please look at the 
pypi package of this package [1] or call the 'bin/develop help'
command which is created during buildout process

commands
--------

Starting the Grok instance with the wiki-application:

  ./bin/zopectl fg

You can use the debug prompt with:

  ./bin/zopectl debug

You can run the tests for the packages with:  

  ./bin/test -s grokcore.formlib
[1] http://pypi.python.org/pypi/mr.developer/0.11

Overview
========

The zc.testbrowser package provides web user agents (browsers) with
programmatic interfaces designed to be used for testing web applications,
especially in conjunction with doctests.

There are currently two type of testbrowser provided.  One for accessing web
sites via HTTP (zc.testbrowser.browser) and one that controls a Firefox web
browser (zc.testbrowser.real).  All flavors of testbrowser have the same API.

This project originates in the Zope 3 community, but is not Zope-specific (the
zc namespace package stands for "Zope Corporation").


Note:
=====

zc.testbrowser.real requires 0.1.8 of MozLab. 0.1.9 does not work
because of changes in the API.


Changes
=======

1.0a4 (2008-03-06)
------------------

 - Fix some packaging bugs.


1.0a3 (2008-03-06)
------------------

 - Break out some interfaces so the various Browser implementations can tell fewer
   lies.

 - Make waiting for asynchronous events (like page loads) explicit.

1.0a2 (2008-02-15)
------------------

 - Bugfix: removed pdb invocation on javascript error

 - Bugfix: text content types where wrapped in html tags in testbrowser.real

 - Bugfix: getLink did not wait until page is loaded in testbrowser.real


1.0a1 (2007-09-28)
------------------

 - First release under new name (non Zope-specific code extracted from
   zope.testbrowser)

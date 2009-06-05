Readme
------

Takes an arbitrary object and syncs it through SVN.

This means a serialization to text, and a deserialization from text.

The text is stored in a SVN checkout. Newly appeared texts are svn added,
removed texts are svn removed. svn move and svn copy are not supported. They
will instead cause a svn delete/svn add combination.

An svn up can be performed. Any conflicting files will be noted and
can be resolved (automatically?).

An svn up always takes place before an svn commit.

An svn sync from the server will main all files that have changed will
be updated in the ZODB, and all files that have been deleted will be
removed in the ZODB. Added files will be added in the ZODB.

Note
----

Currently it is not recommended to use this package in a non-Grok Zope
3 application. This is because Grok turns off certain security checks,
and this is not a behavior you likely wish for in your application.

We are working on ways to make this package work better in an
otherwise non-Grok Zope 3 application, but we're not there yet.

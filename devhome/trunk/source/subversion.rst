Zope Subversion Repository
==========================


Read-only checkouts
-------------------

Anyone can track Zope changes with a read-only checkout of the sources - here
are instructions for hooking it up.

There are several top-level modules in the repository - chief among them is the
Zope sources - we'll use them for our example. You can browse them all at
http://svn.zope.org/

Read-only access is via Subversion svnserve access. Here's how you can do your
initial checkout.

For a Zope 2 trunk checkout::

    svn co svn://svn.zope.org/repos/main/Zope/trunk Zope

For a Zope 2.11 checkout::

    svn co svn://svn.zope.org/repos/main/Zope/branches/2.11 Zope

For a Zope 2.10 checkout::

    svn co svn://svn.zope.org/repos/main/Zope/branches/2.10 Zope

etc.

For a Zope 3 trunk checkout::

    svn co svn://svn.zope.org/repos/main/Zope3/trunk Zope3

For a Zope 3.4 checkout::

    svn co svn://svn.zope.org/repos/main/Zope/branches/3.4 Zope

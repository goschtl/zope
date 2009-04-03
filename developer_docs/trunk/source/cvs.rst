CVS access
----------

.. note::

   This document is only of importance if you are interested for checking
   out older Zope 2 versions (before Zope 2.8). The current codebase
   is now maintained in our Subversion repository
  

Anyone can track Zope changes with a read-only checkout of the sources - here
are instructions for hooking it up.

There are several top-level modules in the archives - chief among them is the
Zope sources - we'll use them for our example.

Read-only access is via CVS pserver mode.

Before you can check anything out, you must have done a CVS "login" to the CVS
pserver. You only need to login once per repository per account. To login::

     >>> cvs -d :pserver:anonymous@cvs.zope.org:/cvs-repository login

You will be prompted for a password - anything will satisfy the prompt,
including an empty line.

(In the command, The -d option identifies the repository, indicating pserver
mode, user anonymous, host cvs.zope.org, and directory /cvs-repository.)

You only need to log in once - it causes a file named .cvspass, with the login
info, to be created in your home directory. All subsequent access to that
repository will use the stashed info.

Once your login is established, you can do your initial check out::

    >>> cvs -z7 -d :pserver:anonymous@cvs.zope.org:/cvs-repository checkout Zope

(-z7 says to use a substantial level of compression, balancing CPU and network
bandwidth. Note It's Zope, no longer Zope2. The section is not maintained, and
will eventually be removed.)

This should issue lots of check out messages, creating a directory named Zope,
with the entire distribution inside it. The initial checkout creates a copy of
the source files together with some CVS bookkeeping, in directories all named
CVS.

Once you've done these initial steps, you can stay current by cd'ing into any
of the created Zope subdirectories and typing:

    >>> cvs -q up -P -d

(-q says not to spew about unchanged files, -P says to prune empty (eg,
obsolete) directories, and -d says to check out newly added directories. In a
pinch, you could just do a cvs up, but: you won't get new directories, nor will
defunct directories be removed, you'll get lots of unnecessary messages...)

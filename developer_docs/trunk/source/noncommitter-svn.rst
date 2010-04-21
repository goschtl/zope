Contributing as a Non-Committer using Subversion
================================================

Even without commit access to the Zope Subversion repository (see
:ref:`becoming-a-committer`), you can still use Subversion to contribute to
Zope projects, using a read-only checkout of the project's sources.

.. _read-only-subversion-checkout:

How-To:  Get a Read-only Subversion Checkouts
---------------------------------------------

There are several top-level modules in the repository - chief among them
is the Zope sources - we'll use them for our example. You can browse them
all at http://svn.zope.org/

Read-only access uses Subversion ``svnserve`` server. Here's how you can do
your initial checkout.

For a Zope 2 trunk checkout:

.. code-block:: sh

   $ svn co svn://svn.zope.org/repos/main/Zope/trunk Zope

For a Zope 2.11 checkout:

.. code-block:: sh

   $ svn co svn://svn.zope.org/repos/main/Zope/branches/2.11 Zope

For a Zope 2.10 checkout:

.. code-block:: sh

   $ svn co svn://svn.zope.org/repos/main/Zope/branches/2.10 Zope

etc.

For a Zope 3 trunk checkout:

.. code-block:: sh

   $ svn co svn://svn.zope.org/repos/main/Zope3/trunk Zope3

For a Zope 3.4 checkout:

.. code-block:: sh

   $ svn co svn://svn.zope.org/repos/main/Zope3/branches/3.4 Zope3


.. _subversion-mirrors:

How-To: Get a Read-only Checkout from a Subversion Mirror
---------------------------------------------------------

The `Deutschsprachige Zope User Group (DZUG) <http://www.zope.de>`_ hosts
a read-only `SVN mirror http://svn.zope.de <http://svn.zope.de>`_  that can
be checked out over HTTP.  Using the SVN mirror over HTTP is convinient if you
are behind a firewall which blocks the ``svnserve`` port.  To check out the
Zope2 trunk, for instance:

.. code-block:: sh

  $ svn co http://svn.zope.de/Zope2/trunk.

Note that some Zope modules reference to other parts of the repository
through ``svn:externals`` using the ``svn://`` protocol. You will not be
able to check out such modules correctly: in fact you may encounter timeouts.

You can also browse the official SVN repository through HTTP read-only through
`http://svn.zope.org/repos/main/ <http://svn.zope.org/repos/main/>`_ .


.. _working-in-svn-checkout:

Working inside the Read-only Checkout
-------------------------------------

You should then be able to work inside your checkout, fixing a bug or
adding a feature.  You can use Subversion commands as normal, e.g.:

.. code-block:: sh

   $ svn co svn://svn.zope.org/repos/main/zope.event/trunk event-trunk
   $ cd event-trunk/
   $ svn info
   Path: .
   URL: svn://svn.zope.org/repos/mainzope.event/trunk
   Repository Root: svn://svn.zope.org/repos/main
   ...
   Last Changed Date: 2010-03-26 16:21:39 -0400 (Fri, 26 Mar 2010)

Let's say you wanted ot add a bit of explanation to the :file:`README.txt`
file:

.. code-block:: sh

   $ vi README.txt
   ...

Subversion knows about the changes you made:

.. code-block:: sh

   $ svn stat
   M      README.txt
   $ svn diff
   Index: README.txt
   ===================================================================
   --- README.txt	(revision 8276)
   +++ README.txt	(working copy)
   @@ -6,6 +6,8 @@
 
    - An event publishing system
 
   +- BLAH, BLAH...
   +
    - A very simple event-dispatching system on which more sophisticated
      event dispatching systems can be built. For example, a type-based
      event dispatching system that builds on ``zope.event`` can be found in

You can keep your checkout updated with ongoing changes, too:

.. code-block:: sh

   $ svn up
   U    docs/api.rst
   U    docs/conf.py
   Updated to revision 8673.

and you may have to deal with changes which conflict with those you
have made.

However, because you are working in an anonymous, read-only checkout, you
cannot commit your changes back to the repository.

.. code-block:: sh

   $ svn commit -m "R00l da world."
   svn: Commit failed (details follow):
   svn: Authorizatino failed

Oops, is all your hard work in vain?


.. _submitting-patches-svn:

How-to: Submit a patch from your Subversion checkout
----------------------------------------------------

Once you have fixed the bug or added the feature in your checkout, double-
check that you have touched all the bases (see :ref:`coding-standards`
and :ref:`layout-conventions`).  All is well, the tests pass, you added
documentation for your cool new feature, so it is time to submit the patch.

First, **don't** try to cut and paste the output from ``svn diff`` into an
e-mail message or a web-browser textarea:  such operations usually end up
mangling the line endings or other bits of the diff, and make it impossible
to apply cleanly.  The maintainer who has to do reconstructive surgery on
such a victim may just give up and ignore the patch.

Avoiding the cut-and-paste train wreck is straightforward:  just create
the patch as a file:

.. code-block:: sh

   $ svn diff > /tmp/zope.event-my_cool_feature.patch

And then send or upload that file as an attachment:  mailers and web-browsers
are nearly as good at leaving attachments alone as they are at destroying
sensitive inline text!

The preferred place to submit patches is to the project's Launchpad bugtracker
(see :ref:`zope-bugtrackers` for how to find your projects tracker).
You will need to register for a Launchpad account, but you should then be
able to create a new issue and upload your patch file to it. 

Good titles, descriptions, and other metdata on the issue
should help it get the attention of the right maintainer for the project:
if you don't hear back fairly quickly, try asking on the appropriate IRC
channel for your project (see :doc:`irc-channels`), or follow up to the
project developers' maininglist (see :doc:`mailinglists`).

Becoming a Committer
====================

Applying for Committer Status
-----------------------------

1. Mail webmaster@zope.org for a new user account at www.zope.org.
   Pick a user id that is a valid Unix user id. Include this id when
   you fill out the committer agreement form.

2. Print, fill out and sign the
   `Zope Committer Agreement <http://foundation.zope.org/agreements>`_

3. Submit the agreement to the Zope Foundation. This can be done by
   either email, fax or post (in order from fastest to slowest).

   The contact details can be found on the
   `Zope Foundation website <http://foundation.zope.org/about>`_.

4. Wait for an acknowledgement. If you don't get this in a reasonable amount
   of time, then ask back on the Zope Foundation list
   (foundation-info@zope.org) or try to contact a member of the repository
   committee (Andreas Jung and Christian Theune).

5. Deposit your SSH public key(s) as described in :ref:`deposit-ssh-pubkey`

6. Get a :doc:`writeable checkout <subversion-writable-checkouts>`.

.. _deposit-ssh-pubkey:

Depositing your SSH public key(s)
---------------------------------

Your SSH public key(s) must be uploaded using the application at: 
https://cvs.zope.org/upload-key.html

When you go to that url, you'll get a basic auth login prompt.  Use your
www.zope.org login and password.

Your keys can use RSA or DSA, ssh v1 or v2. If the file being uploaded
contains more than one public key, it should be formatted as if it
were an authorized_keys file.

You can revisit the key deposit page any time to put in new keys.
Make sure you submit all keys that you wish to have work in any file
that you upload as your previous upload will be overwritten.

Subscribe to the Mailing Lists
------------------------------

Active Zope 2 committers should subscribe to the `zope-dev mailinglist
https://mail.zope.org/mailman/listinfo/zope-dev`_.

They should also either subscribe to the `zope2-tracker notifications
mailinglist <http://mail.zope.org/mailman/listinfo/zope2-tracker>`_. 
(this list receives notifications from Launchpad for each updated bugtracker
issue in the ``zope2`` project), or ask to be added to the ``zope2-dev``
team on Launchpad.

Grok committers should be subscribed to the `grok-dev mailinglist
<https://mail.zope.org/mailman/listinfo/grok-dev>`_.

Bluebream committers should be subscribed to the `bluebream mailinglist
<https://mail.zope.org/mailman/listinfo/bluebream>`_.

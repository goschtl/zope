Becoming a contributor
----------------------

1. Get an account at http://www.zope.org.  Pick a user id that is a valid Unix
   user id. Include this id when you fill out the contributor form.

2. Print, fill out and sign the `Zope Committer Agreement <http://foundation.zope.org/agreements>`_

3. Submit the agreement to the Zope Foundation.
   This can be done by either email, fax or post (in order from fastest to slowest).
   The contact details can be found on the `Zope Foundation website <http://foundation.zope.org/about>`_.

4. Wait for an acknowledgement. If you don't get this in a reasonable amount of
   time, then nag jim@zope.com, or J1m on the freenode #zope3 IRC channel.  A
   reasonable time depends on the way the agreement was sent, as described above.

5. Deposit your SSH public key(s) as described in the section below.

6. Do a :doc:`writeable checkout <subversion-writable-checkouts>`.

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










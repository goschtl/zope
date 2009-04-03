Becoming a contributor
----------------------

1. Get an account at http://www.zope.org.  Pick a user id that is a valid Unix
   user id. Include this id when you fill out the contributor form.

2. Print, fill out and sign the `Zope Committer Agreement <http://foundation.zope.org/agreements>`_

3. Submit the agreement in one of 3 ways as a scanned copy or through fax
   or through postal mail to the `Zope Foundation <http://foundation.zope.org/about>`_

4. Wait for an acknowledgement. If you don't get this in a reasonable amount of
   time, then nag jim@zope.com, or J1m on the freenode #zope3 IRC channel.  A
   reasonable time depends on the way the agreement was sent, as described above.

4. Upload your SSH public key at: https://cvs.zope.org/upload-key.html

   When you go to that page, you'll get a basic auth login prompt.  Use your
   www.zope.org login and password.

   If you have trouble, **do not ask Jim Fulton for help.**  Ask for help on
   the IRC channels. People there may ask me to look at ssh logs on the server or
   at the uploaded keys, as I am able to access those.

   One thing to keep in mind is that the user id you use to access the
   subversion and CVS repositories is your zope.org user id.  This means that you
   might have to specify a id explicitly. I know of two ways to do this:

   - Include it in the subversion url: svn+ssh://your_zope_org_id@svn.zope.org/repos/main/some_path

   - Specify the user if to use for svn.zope.org (or cvs.zope.org) in your SSH configuration.
     See the SSH documentation for details.


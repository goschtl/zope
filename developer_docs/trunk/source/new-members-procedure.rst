Procedure for accepting new committer applications
--------------------------------------------------

.. note:: This document defines the procedure for accepting new SVN committer 
   applications handled by the Zope Foundation committer committee
   (Christian Theune, Andreas Jung).

1) Check application form

   - Check readability of the scanned application form
   - If applicant and reference committer are (well)-known, proceed
     with procedure. Otherwise ask the reference committer about
     the applicant. Note that the reference committer must be an
     active committer.

2) Create SVN account for new committer::

   $ ssh svn.zope.org
   $ sudo /usr/sbin/newsvnuser <zopeorg-name> <Firstname> <...> <Lastname>

3) Send notification mail to:

   - applicant  (TO:)
   - reference committer  (CC:)
   - foundation-info@zope.org list (CC:)

   containing:: 

       Subject: Your zope.org SVN account was approved

       Dear <<<NAME>>>,

       on behalf of the Zope foundation I'm happy to tell you that your Zope
       Contributor Agreement was received and approved. <<<REFERENCE>>> was
       given as the reference committer.

       Using your zope.org user account, you're now able to check in code
       into svn.zope.org.

       One last step, though: you need to deposit your SSH public key(s) as
       described:
       http://docs.zope.org/developer/becoming-a-committer.html

       Best regards,
       <<<SENDER>>>


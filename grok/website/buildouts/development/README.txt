Developing the Grok web site
----------------------------

To create a development environment to start working on the Plone portion
of the Grok web site:

 * Checkout the base buildout configuration from SVN:

   svn co svn://svn.zope.org/repos/main/grok/website/buildouts/development \
   grokplone

 * Checkout the plonetheme.grok package in your src directory:

    svn co https://svn.plone.org/svn/collective/plonetheme.grok/trunk \
    src/plonetheme.grok

 * Run the buildout:

   cd grokplone
   python bootstrap.py
   ./bin/buildout

 * Start up Zope:

   ./bin/instance fg

 * Create a new Plone instance using the ZMI and choose the "Grok theme for
   Plone 3" extension profile. The username and password is grok:grok.

   http://localhost:8080/manage

 * Makes some changes in the src directory.
   Restart some Zopes.
   Do some tests.
   Commit!


To-Do
-----

 * Create a policy product that pulls in plonetheme.grok and installs
   PloneHelpCenter. Adjust the buildout.

 * The development buildout should install up some sample content to theme
   against, etc.

 * Create a production buildout.

 * svn checkouts, should we use a buildout recipe to do this?

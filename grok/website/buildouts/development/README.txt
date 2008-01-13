Developing the Grok web site
----------------------------

To create a development environment to start working on the Plone portion
of the Grok web site:

 * Checkout the base buildout configuration from SVN::

    svn co svn://svn.zope.org/repos/main/grok/website/buildouts/development \
    grokplone

 * Checkout the gzo.plonepolicy and gzo.plonesmashtheme packages into your
   src directory. Replace svn:// with svn+ssh://username if you are going
   to commit changes::

    $ cd grokplone

    $ svn co svn://svn.zope.org/repos/main/gzo.plonepolicy/trunk \
      src/gzo.plonepolicy

    $ svn co svn://svn.zope.org/repos/main/gzo.plonesmashtheme/trunk \
      src/gzo.plonesmashtheme
	
 * Run the buildout::

    $ python bootstrap.py
    $ ./bin/buildout

 * Start up Zope::

    $ ./bin/instance fg

 * Create a new Plone instance using the ZMI and choose the "Grok Site Policy"
   extension profile. The username and password is grok:grok::

     http://localhost:8080/manage

 * Navigate to the Site Setup > Add/Remove Products and install the 
   "Grok Site Policy" Product.

   (can we have this install called when we choose the 'Grok Site Policy'
    in the previous step?)

 * Makes some changes in the src directory.
   Restart some Zopes.
   Do some tests.
   Commit!


To-Do
-----

 The latest home for To-Do notes is currrently at:
 
 http://www.openplans.org/projects/zorg-redux/grok-zope-org

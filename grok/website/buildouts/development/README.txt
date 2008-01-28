Developing the Grok web site
----------------------------

To create a development environment to start working on the Plone portion
of the Grok web site:

 * Checkout the base buildout configuration from SVN::

    svn co svn+ssh://svn.zope.org/repos/main/grok/website/buildouts/development \
    grokplone
	
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

   (We should be able to have this installed when we choose the
    'Grok Site Policy' in the previous step? It's got bugs ATM.)

 * Make an export of the 'public_website' Folder of the production site
   (maybe we should make one of this available somewhere)
   and copy that into ./parts/instance/import/. Use the ZMI to import this
   content into your development instance. You may need to poke the
   portal_catalog for a re-index.
 
 * Makes some changes in the src directory.
   Restart some Zopes.
   Do some tests.
   Commit!


To-Do
-----

 The latest home for To-Do notes is currrently at:
 
 http://www.openplans.org/projects/zorg-redux/grok-zope-org

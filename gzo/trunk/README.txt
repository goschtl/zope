==========================================================
Information about the Plone instance running grok.zope.org
==========================================================

Plone Instance:

	/var/zope/instances/gzo

Plone ZMI:

	http://grok.zope.org/site-admin/manage_main

Apache Configuration:

	/etc/httpd/vhosts/grok/plone.grok.quintagroup.com.conf

Reload Apache Configuration:

/etc/init.d/httpd reload


Neanderthal II Sprint
---------------------

- Migration from Plone 3.0.5 to Plone 3.1.7

- Replace the Plone search box to a google search based search box.
  This way, we are able to search inside the Sphinx based documentation.

- Updated Message of a day on the server

- gzo buildout added to svn


Plone 3.0.5 Instance (old)
--------------------------

/var/zope/gzo

gzo.plonepolicy and gzo.plonesmashtheme were tagged as 0.1 in the SVN.


Plone 3.1.7 Instance (current)
------------------------------

Attempts to migrate to the latest Plone version failed so far, because
the body text of some of the content objects inside the PloneHelpCenter
(documentation) is lost during migration.

Nevertheless the gzo instance runs on Plone 3.3 without any problems.


Plone 3.3 Instance (upgrade)
----------------------------

Since the patched version of PHC in the products directory seems to be
the problem, the first thing to do would be to migrate PHC to a newer
version and remove the patches.

If patches of PHC are necessary, we should use collective.monkeypatcher
to override classes or methods.


Todo/Ideas:
-----------

- Use optilude's über buildout (zeo, varnish)
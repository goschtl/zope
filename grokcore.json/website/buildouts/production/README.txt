Administering the Grok web site
-------------------------------

This buildout manages the Plone installation. It should be run on the
grok.zope.org server at /var/zope/grokplone.

The Zope instance serving up the Plone site is running on port 7000,
and is proxied to using a RewriteRule in the system installation
of Apache 2.

The Plone content for the Grok web site is located at /plone/public_website/
inside the Zope instance.

There is a re-write rule to allow you to access the root of the Plone instance
at:

http://grok.zope.org/site-admin/plone/


ToDo
----

Buildout specific known-issues:

 * Package up some eggs!

   Currently we are deploying svn checkouts for the gzo parts.

Things to do to make sure the production site is a happy site:

 * backups! Off-site? Where?

 * caching. Varnish?

 * log analysis.
 
   Quintagroup provides awstats at:
   http://grok.zope.org/stats/

 * sysadmin support. More than one sysadmin should be familiar
   with the configuration and be able to fix bits if things go south.

 * sysadmin review. What have we overlooked in the maintenance of the server?
   Running security updates, etc?

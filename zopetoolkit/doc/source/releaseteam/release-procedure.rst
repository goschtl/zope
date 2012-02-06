Release procedure
=================

.. note::

   This is internal documentation for the Zope Toolkit release team
   to create official Zope Toolkit releases.

Steps for creating a new release
--------------------------------

- Get a checkout of svn+ssh://svn.zope.org/repos/main/zopetoolkit

- check the buildbots for failing tests

- Check the ztk-versions.cfg and zopeapp-versions.cfg file for outdated or
  updated packages and update version information where necessary. Run::

    bin/checkversions -l 2 ztk-versions.cfg
    bin/checkversions -l 2 zopeapp-versions.cfg

  to check them. Give the buildbots a day to test the new set on all platforms.

  .. note::

     This will change depending on ccomb's buildbot to automatically update
     versions.

- review index.rst

- tag the release. For example::

    svn cp svn+ssh://svn.zope.org/repos/main/zopetoolkit/branches/1.0
    svn+ssh://svn.zope.org/repos/main/zopetoolkit/tags/1.0.1

- create the release specific download index on download.zope.org
  (requires login credentials on download.zope.org. In case of
  problems contact Jens Vagelpohl)

  - login to download.zope.org

  - change to user ``zope``::

     sudo su - zope

  - create the download index (e.g. for Zope Toolkit 1.0a1)::

    /home/zope/zope2index/bin/ztk_kgs tags/1.0a1 /var/www/download.zope.org/zopetoolkit/index/1.0a1

- Send an announcement on the zope-dev list (based on previous ones), and spread
  the info.

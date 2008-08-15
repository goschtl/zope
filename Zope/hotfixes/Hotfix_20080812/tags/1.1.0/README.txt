Hotfix-20080812 README

    PythonScripts in Zope 2 can be misused for shutting down a complete Zope 2
    instance or misused for a local denial-of-service attack. This issue affects
    only those Zope 2 instances where users have unrestricted access to the ZMI and
    the ability to edit PythonScripts. This should usually not be the case for
    instances where the Manager access is granted only to trusted persons. 

    A PythonScript containing

          raise SystemExit

    will immediately shutdown the current Zope instance

    A PythonScript containing

          return 'foo'.encode('test.testall')

    would import the 'test' module of Python and execute all tests
    (could be misused for a denial-of-service attack). Also other modules
    could possibly be imported.


  Affected Versions

    - Zope 2.7.0 to Zope 2.11.2
    
    - Earlier versions of Zope 2 are affected as well, but no new
      releases for older major Zope releases (Zope 2.6 and earlier) will
      be made. This Hotfix may work for older versions, but this has not
      been tested.
    
  Installing the Hotfix

    This hotfix is installed as a standard Zope2 product.  The following
    examples assume that your Zope instance is located at
    '/var/zope/instance':  please adjust according to your actual
    instance path.  Also note that hotfix products are *not* intended
    for installation into the "software home" of your Zope.

      1. Unpack the tarball / zipfile for the Hotfix into a temporary
         location::

          $ cd /tmp
          $ tar xzf ~/Hotfix_20080812.tar.gz

      2. Copy or move the product directory from the unpacked directory
         to the 'Products' directory of your Zope instance::

          $ cp -a /tmp/Hotfix_20080812/ /var/zope/instance/Products/

      3. Restart Zope::

          $ /var/zope/instance/bin/zopectl restart

  Uninstalling the Hotfix

    After upgrading Zope to one of the fixed versions, you should remove
    this hotfix product from your Zope instance.

      1. Remove the product directory from your instance 'Products'::

          $ rm -rf /var/zope/instance/Products/Hotfix_20080812/

      2. Restart Zope::

          $ /var/zope/instance/bin/zopectl restart

  References

      http://www.zope.org/advisories/advisory-2008-08-12

Hotfix-20060705 README

    This hotfix corrects an information disclosure vulnerability in Zope2,
    due to Zope2's use of the docutils module to parse and render
    "restructured text".

    Sites which allow untrusted users to create restructured text as
    through-the-web content should apply this hotfix.
    
    The hotfix may be removed after upgrading to a version of Zope2 more
    recent than this hotfix.

  Affected Versions

    - Zope 2.7.0 - 2.7.8

    - Zope 2.8.0 - 2.8.7

    - Zope 2.9.0 - 2.9.2

  Installing the Hotfix

    This hotfix is installed as a standard Zope2 product.  The following
    examples assume that your Zope instance is located at
    '/var/zope/instance':  please adjust according to your actual
    instance path.  Also note that hotfix products are *not* intended
    for installation into the "software home" of your Zope.

      1. Unpack the tarball / zipfile for the Hotfix into a temporary
         location::

          $ cd /tmp
          $ tar xzf ~/Hotfix_20060704.tar.gz

      2. Copy or move the product directory from the unpacked directory
         to the 'Products' directory of your Zope instance::

          $ cp -a /tmp/Hotfix_20060704/ /var/zope/instance/Products/

      3. Restart Zope::

          $ /var/zope/instance/bin/zopectl restart

  Uninstalling the Hotfix

    After upgrading Zope to one of the fixed versions, you should remove
    this hotfix product from your Zope instance.

      1. Remove the product directory from your instance 'Products'::

          $ rm -rf /var/zope/instance/Products/Hotfix_20060704/

      2. Restart Zope::

          $ /var/zope/instance/bin/zopectl restart

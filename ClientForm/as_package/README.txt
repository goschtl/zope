What is this?
-------------

This directory is a place for holding the sliced-and-diced version
of ClientForm used in Zope2 SVN checkouts.  Those checkouts want to
pull in ClientForm (the module) but as an 'svn:external' (which requires
a directory.

So, we "packageize" the module here, making it the __init__.py of a
same-named package.

Using a newer release
---------------------

In order to use a newer release of the ClientForm package in Zope2,
follow this recipe.

 1. From the directory where you unpacked the tarball::
 
    $ export NEW_VERSION=0.2.10  # for example
    $ export ZSVN=svn+ssh://svn.zope.org/repos/main
    $ svn import -m "Import ClientForm $NEW_VERSION" \
      $ZSVN/ClientForm/tags/$NEW_VERSION

 2. Create a new 'as_package' directory:
 
    $ svn mkdir -m "Package-ize ClientForm $NEW_VERSION" \
      $ZSVN/ClientForm/as_package/$NEW_VERSION

 3. Copy 'ClientForm.py' from the import to the 'as_package' directory::

    $ svn mkdir -m "Package-ize ClientForm $NEW_VERSION" \
      $ZSVN/ClientForm/tags/$NEW_VERSION/ClientForm.py \
      $ZSVN/ClientForm/as_package/$NEW_VERSION/__init__.py

 4. Update the svn:external in the Zope2 checkout::

    $ svn co $ZSVN/Zope/trunk Zope-trunk
    ...
    $ cd Zope-trunk
    $ svn propedit svn:externals lib/python
    ...
    $ svn commit -m "Use ClientForm $NEW_VERSION"

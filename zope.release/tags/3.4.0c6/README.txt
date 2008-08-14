===============================
Zope 3 Controlled Package Index
===============================

This package has been developed to support the maintenance of a stable set of
Zope project distributions. It manages the controlled packages configuration
file and supports the generation of buildout configuration files that can be
used by developers.

Another use of this package is to use it for testing new distributions against
the index. Here is the workflow for testing a new package against stable set:

1. Install the correct version of this package.

   (a) Download the version of this package that manages the stable set that
       you are interested in. For the Zope 3.4 release, a 3.4 branch exists::

         $ svn co svn://svn.zope.org/repos/main/zope.release/branches/3.4 zope3.4
         $ cd zope3.4

   (b) Bootstrap the checkout::

         $ python ./bootstrap.py

   (c) Run buildout to create the scripts::

         $ ./bin/buildout

   (d) Run the ``buildout.cfg`` generation script to build a configuration
       file that can be used for testing:

         $ ./bin/generate-buildout

2. From the generated configuration file, you can now build a testing
   environment.

   (a) Enter the test directory and create a buildout:

         $ cd test
         $ python ../bootstrap.py
         $ ./bin/buildout

   (b) Run all the tests to verify that all tests are initially passing:

         $ ./bin/test -vpc1

3. Modify the ``buildout.cfg`` to look for your the new distribution to be
   tested:

   (a) Change the version number of the package of interest in the "versions"
       section.

   Alternative:

   (a) Check out the new distribution from SVN.

   (b) Add a "develop path/to/my/package" line in the "buildout" section of
       ``buildout.cfg``.

4. Run the tests, making sure that they all pass.

5. Modify ``controlled-packages.cfg`` to reference the new version.

   (a) Find the package that you are interested in and add the new of the
       package in the `versions` attribute of the package's section.

   (b) In the `[KGS]` section, increase the version number in the `version`
       attribute.

6. Upload the new KGS release::

     $ cd ..
     $ ./bin/upload

   Once the files are uploaded, a crontab-job, running every minute, will
   detect the changes in ``controlled-pages.cfg`` and will generate the new
   controlled package pages.

7. Update the svn:externals in the Zope3 3.4 branch:

     $ svn co svn+ssh://svn.zope.org/repos/main/Zope3/branches/3.4 Zope3-3.4
     $ ./bin/update-tree
     $ cd Zope3-3.4
     $ svn diff
     $ svn commit

Note: I think the process is still a tiny bit too long. I probably write a
script that makes testing a new version of a package easier, but let's see
whether this process is workable first.

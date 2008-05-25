================
z3c.securitytool
================

z3c.securitytool is a Zope3 package aimed at providing component level
security information to assist in analyzing security problems and to
potentially expose weaknesses. The goal of the security tool is to
provide a matrix of users and their effective permissions for all available
views for any given component and context. We also provide two further
levels of detail. You can view the details of how a user came to have
the permission on a given view, by clicking on the permission in the matrix.

.. image::
  http://farm3.static.flickr.com/2318/2521732872_81a709e3db_m.jpg
  :height: 200
  :width: 400
  :target: http://flickr.com/photos/blackburnd/

=================
Demo Instructions
=================

You can run the demo by downloading just the securitytool package

- ``# svn co svn://svn.zope.org/repos/main/z3c.securitytool/trunk securitytool``
- ``# cd securitytool``
- ``# python bootstrap.py``
- ``# ./bin/buildout``
- ``# ./bin/demo fg``

Then access the demo site using:

- http://localhost:8080/++skin++SecurityTool/securityMatrix.html
- user: admin
- password: admin

There are some folders added with permissions and roles applied to show
the settings in the demo. 

- http://localhost:8080/++skin++SecurityTool/Folder1/securityMatrix.html
- http://localhost:8080/++skin++SecurityTool/Folder1/Folder2/securityMatrix.html

These permissions should mirror what you see in the @@grant.html views

- http://localhost:8080/Folder1/Folder2/@@grant.html
- http://localhost:8080/Folder1/@@grant.html

``(These settings are  added when the database is first opened``
   ``You can find these settings in demoSetup.py)``


==============================================
How to use the securityTool with your project:
==============================================
Remember this is a work in progress.

1. Add the z3c.securitytool to your install_requires in your
   setup.py. 
2. Add the <include package="z3c.securitytool"/> to your site.zcml
3. Use the skin `++skin++SecurityTool` to access securityTool pages
4. Append @@securityMatrix.html view to any context to view the permission
   matrix for that context using the security tool skin.

  For example:
  http://localhost:8080/++skin++SecurityTool/Folder1/@@securityMatrix.html



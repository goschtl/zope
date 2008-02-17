
===================================================================
  Zope3 SecurityTool (z3c.securitytool)
===================================================================

  This package is used as a tool to view all the permissions for any
  view in any context. These permissions are gathered from the roles
  groups and of course directly provided permissions.


  ===================================================================
  Demo Instructions
  ===================================================================

  You can run the demo by downloading just the securitytool package

    $ svn co svn://svn.zope.org/repos/main/z3c.securitytool/trunk securitytool
    $ cd securitytool
    $ python bootstrap.py
    $ ./bin/buildout
    $ ./bin/demo fg

  Then access the demo site using:
    http://localhost:8080/securityMatrix.html

  There are some folders added with permissions and roles applied to show
  the settings in the demo. 

   - http://localhost:8080/Folder1/securityMatrix.html
   - http://localhost:8080/Folder1/Folder2/securityMatrix.html


   ( These settings are  added when the database is first opened
     You can find these settings in demoSetup.py )


  If  you select the ConcordTimes skin the same permissions will be
  displayed as the permissions described in README.txt functional 
  test


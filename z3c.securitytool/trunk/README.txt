
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

    http://localhost:8080/@@vum.html


  If  you select the ConcordTimes skin the same permissions will be
  displayed as the permissions described in README.txt functional 
  test

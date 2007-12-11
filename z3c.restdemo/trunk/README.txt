==================================
Demo Applications for ``z3c.rest``
==================================

This package contains several small demo applications for the ``z3c.rest``
package.

* A simple echo demo.


Running the Demo out of the box
-------------------------------

You can also run the demo directly without manually installing Zope 3::

  $ svn co svn://svn.zope.org/repos/main/z3c.restdemo/trunk restdemo
  $ cd restdemo
  $ python bootstrap.py
  $ ./bin/buildout
  $ ./bin/demo fg

Then access the demo site using:

  http://localhost:8080/

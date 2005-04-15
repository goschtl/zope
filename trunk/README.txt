Zelenium Product README

  Overview

    This product allows developers to create TTW Selenium test suites
    inside their Zope instance, in order to to browser-based functional
    testing of their site.


  Installing the Product

    1. Unpack the tarball in a temporary location.

    2. Copy or move the 'Zelenium' directory to the 'Products' directory
       of your INSTANCE_HOME.

    3. Restart Zope.


  Using Zelenium

    You can add a 'Zuite' object at any location within your Zope
    site.  It behaves as a standard ordered folder, with a couple of 
    differences:

      - It's 'index_html' is the "TestRunner.html" view familiar
        from Selenium.

      - It derives the test suite (in the upper left corner iframe)
        from all OFS.Image.File objects whose names start with 'test'.
        You can use the OrderedFolder support to modify the order in
        which the test case files are run.

      - It provides a "Zip" action, which allows you to export the
        test suite, all test cases, and the supporting Selenium
        Javascript / CSS files as a single, self-contained zipfile.


  Adding Tests

    Tests are just 'File' instances whose names begin with 'test'.
    They should have a content type of 'text/html', and should contain
    a table which defines the steps which make up the test case.

    See http://selenium.thoughtworks.com/testrunner.html for documentation
    on the table structure and the Selenese language.


  Exporting an Archive

    On the "Zip" tab, supply a filename and click the "Download" button.
    The Zuite object will construct a zip file with the following
    contents:

      'index.html' -- the "TestRunner.html" framework page

      'TestSuite.html' -- the list of test case files (rendered as
        static HTML)

      'test*" -- your test case files (appending '.html' if the IDs
        do not have extensions)

      Each of the supporting '.js' and '.css' files which drive the
      browserbot.


  Creating a Snapshot

    On the "Zip" tab, supply a filename and click the "Download" button.
    The Zuite object will construct a zip file with the same contents
    described above, and then save it as a File object in its own contents.

------------------------------------------------------------------------------
Test Recorder
------------------------------------------------------------------------------

The test recorder is a browser-based tool to support the rapid development 
of functional tests for Web-based systems and applications.

This package is designed to be deployable in Zope 2 or Zope 3 applications.

For a Zope 2 system, drop this package into the products directory of the 
Zope instance and restart the instance. After restart, it will be possible 
to add a 'Test Recorder' object in the ZMI. The Test Recorder Zope object 
mainly provides the ability to traverse to the html and .js files that 
make up the recorder.

In a Zope 3 system, you only need to register the 'html' directory of 
this package as a resourceDirectory using ZCML. The following example ZCML 
directive will register the test recorder resources and make them available 
through a resource URL such as '/@@/recorder/index.html'.

    <browser:resourceDirectory
      name="recorder"
      directory="html"
      layer="default"
      />




Needs more docs.

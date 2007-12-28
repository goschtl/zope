Some notes about setting this buildbot up:

- The `static` directory needs to be made available through some webserver.
  The CSS file pulls in the images relative to the place where the CSS is
  located. The address of the CSS file is currently hard coded.

================================
bsquare - buildbot for buildouts
================================

This package provides a buildout configuration and utilities to automatically
monitor a subversion repository defining zc.buildout-based projects.

It also defines an alternative comprehensive view  (inspired by cruise control)
accessiable via /cruise.

Installation
------------

- Install this package using standard distutils functionality:

      $ python setup.py install

- Set up a buildbot master and configure the master.cfg like this:

      $ cat > master.cfg
      import bsquare.master

      config = bsquare.master.configure('http://svn.example.com/repository')

  You can then edit the config object like the normal buildout master's
  configuration (adding the base URL, your contact information, slaves, etc ...)

- Set up a cron-job to execute the `update-config.sh` script with two arguments:
  your buildbot master`s directory and the subversion base url:

  $ update-config.sh /home/foo/buildbot-master http://svn.example.com/repository/

- In your master's `public_html` directory, you should
  edit the `index.html` to allow access to the cruise-control-like interface.

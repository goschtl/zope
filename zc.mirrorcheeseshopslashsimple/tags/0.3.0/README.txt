Setting up a PyPI "simple" index
================================

This package provides a mirror for the PyPI simple interface,
http://cheeseshop.python.org/simple/.

To set up a mirror:

- install this package using setuptools (easy_install, buildout, etc.)
  so that the script, update-mirror script is installed.

- Create the directory to hold the mirror somewhere in a web-server
  documents area.

- Run the update-mirror script passing the name of the mirror
  directory.

  This will initialize the mirror.  It takes about 15 minutes for me.

- Set up a cron job to run update-mirror periodically. I run it once a
  minute. Checking for updates is very fast.

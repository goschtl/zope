Setting up a PyPI "simple" index
================================

This package provides a mirror for the PyPI simple interface,
http://cheeseshop.python.org/simple/.

To set up a mirror:

- install this package using setuptools (easy_install, buildout, etc.)
  so that the script, pypimirror script is installed.

- create your mirror configuration file maybe based on config.cfg.sample

- Run the pypimirror script passing the name of the mirror configuration
  file

  This will initialize the mirror.

- Set up a cron job to run update-mirror periodically.

BlueBream Website
=================

This is the content for BlueBream website: http://bluebream.zope.org

Directories and Files
---------------------

Layout::

  website/
  |-- bin/
  |   |-- buildout*
  |   `-- makesite.sh*
  |-- bootstrap.py
  |-- buildout.cfg
  |-- docs/
  |   `-- v1.0/
  |       |-- conf.py
  |       |-- index.rst
  |       |-- Makefile
  |       |-- _static
  |       `-- _templates
  |-- examples/
  |-- htdocs/
  |-- main/
  |   |-- blue
  |   |-- conf.py
  |   |-- index.rst
  |   |-- Makefile
  |   |-- _static
  |   `-- _templates
  |-- README.txt
  |-- templates/
  |   `-- makesite_sh.in*
  `-- versions.cfg

- ``bin/buildout*`` -- Run this script whenever ``buildout.cfg``
  is changed

- ``bin/makesite.sh*`` -- To create the site, output inside ``htdocs/``
  directory

- ``bootstrap.py`` -- Run this script initially to bootstrap the buildout

- ``buildout.cfg`` -- The Buildout configuration

- ``docs/`` -- All the docs goes here, now only ``v1.0``

- ``docs/v1.0`` -- Documentation for 1.0 release

- ``docs/v1.0/conf.py`` -- The Sphinx conf file for ``v1.0` documentation

- ``docs/v1.0/index.rst`` -- The main index file all other pages are
  linked from here

- ``docs/v1.0/Makefile`` -- Run make to create HTML for 1.0 docs (It is
  recommended to use ``bin/makesite.sh*`` as it creates all output
  including main site)

- ``docs/v1.0/_static`` -- Static files for docs goes here (empty now)

- ``docs/v1.0/_templates`` -- Templates for docs goes here.

- ``examples/`` -- All example code goes here

- ``htdocs/`` -- The website output goes here

- ``main/`` -- The main site content

- ``main/blue`` -- Theme for main site

- ``main/conf.py`` -- The Sphinx conf file for main site

- ``main/index.rst`` -- The main page content

- ``main/Makefile`` -- Run make to create HTML for main site (It is
  recommended to use ``bin/makesite.sh*`` as it creates all
  output including documentation)

- ``main/_static`` -- Static files for main site goes here (empty now)

- ``main/_templates`` -- Templates for main site goes here.

- ``README.txt`` -- This file

- ``templates/`` -- Templates for Buildout (now only one)

- ``templates/makesite_sh.in*`` -- Run this script to generate all site.

- ``versions.cfg`` -- Pin versions of distributions to be used by Buildout


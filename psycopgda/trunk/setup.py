"""Psycopg Database Adapter for Zope 3

This package allows Zope 3 to connect to any PostGreSQL database via
the common Zope 3 RDB connection facilities.
"""

from setuptools import setup, find_packages

# We're using the module docstring as the distutils descriptions.
doclines = __doc__.split("\n")
VERSION = open('version.txt', 'rb').read().strip()

setup(name="psycopgda",
      version=VERSION,
      author="Zope Corporation and Contributors",
      author_email="zope3-dev@zope.org",
      license = "ZPL 2.1",
      platforms = ["any"],
      description = doclines[0],
      long_description = "\n".join(doclines[2:]),
      packages = find_packages(),
      )

"""base classes

$Id$
"""
__docformat__ = 'ReStructuredText'
import StringIO
import base64
import httplib
import logging
import optparse
import os
import pkg_resources
import subprocess
import sys
import urllib2
import urlparse

from zope.wineggbuilder import base

LOGGER = logging.Logger('build')

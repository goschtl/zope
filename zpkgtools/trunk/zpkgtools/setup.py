##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Generator for distutils setup.py files."""

import os.path

from StringIO import StringIO


# These are both attributes of the publication data object and keyword
# arguments to setup().

STRING_ATTRIBUTES = [
    "name",
    "version",
    "license",
    "author",
    "author_email",
    "maintainer",
    "maintainer_email",
    "description",
    "long_description",
    "download_url",
    ]

LIST_ATTRIBUTES = [
    "keywords",
    "classifiers",
    ]

def generate(directory, publication, version, packageinfo=None):
    setup_py = os.path.join(directory, "setup.py")
    f = open(setup_py, "w")
    try:
        generate_py(f, publication, version, packageinfo)
    finally:
        f.close()

    # We don't always need to generate a setup.cfg, so use a StringIO
    # as an intermediate:
    f = StringIO()
    generate_cfg(f, publication, version, packageinfo)
    text = f.getvalue()
    if text.strip():
        setup_cfg = os.path.join(directory, "setup.cfg")
        f = open(setup_cfg, "w")
        try:
            f.write(CONFIG_HEADER)
            f.write(text)
        finally:
            f.close()


def generate_py(f, publication, version, packageinfo):
    """Generate the setup.py for a release."""
    print >>f, HEADER
    print >>f, "setup(version=%r," % version
    for name in STRING_ATTRIBUTES:
        dumpString(f, publication, name)
    if publication.platforms:
        print >>f, "      platforms=%r," % ", ".join(publication.platforms)
    for name in LIST_ATTRIBUTES:
        dumpList(f, publication, name)
    print >>f, "      )"


def generate_cfg(f, publication, version, packageinfo):
    """Generate the setup.cfg for a release."""
    # For now, do nothing.


def dumpString(f, publication, name):
    value = getattr(publication, name)
    if value is not None:
        if "\n" in value:
            # deal with multiline values
            pass
        else:
            print >>f, "      %s=%r," % (name, value)


def dumpList(f, publication, name):
    value = getattr(publication, name)
    if value:
        print >>f, "      %s=[" % name
        for v in value:
            print >>f, "          %r," % v
        print >>f, "          ],"


HEADER = """\
#! /usr/bin/env python
#
# THIS IS A GENERATED FILE.  DO NOT EDIT THIS DIRECTLY.

from distutils.core import setup
from distutils.core import Extension

"""

CONFIG_HEADER = """\
# THIS IS A GENERATED FILE.  DO NOT EDIT THIS DIRECTLY.

"""

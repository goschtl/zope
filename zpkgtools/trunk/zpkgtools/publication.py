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
"""Support for reading and generating PKG-INFO files.

$Id: publication.py,v 1.1 2004/03/05 21:39:19 fdrake Exp $
"""
from distutils.dist import DistributionMetadata
from distutils.util import rfc822_escape
from email.Parser import Parser
from StringIO import StringIO


# XXX The dump() and dumps() methods are very similar to the
# DistributionMetadata.write_pkg_info() method, but don't constrain
# where the data is written.  Much of this can be discarded if
# portions of the PEP 262 patch (http://www.python.org/sf/562100) are
# accepted.

def dump(metadata, f):
    """Write package metadata to a file in PKG-INFO format."""
    print >>f, "Metadata-Version: 1.0"
    print >>f, "Name:", metadata.get_name()
    if metadata.version:
        print >>f, "Version:", metadata.get_version()
    if metadata.description:
        print >>f, "Summary:", metadata.get_description()
    if metadata.url:
        print >>f, "Home-page:", metadata.get_url()
    if metadata.author:
        print >>f, "Author:", metadata.get_author()
    if metadata.author_email:
        print >>f, "Author-email:", metadata.get_author_email()
    if metadata.maintainer:
        print >>f, "Maintainer:", metadata.get_maintainer()
    if metadata.maintainer_email:
        print >>f, "Maintainer-email:", metadata.get_maintainer_email()
    if metadata.license:
        print >>f, "License:", metadata.get_license()
    if metadata.url:
        print >>f, "Download-URL:", metadata.url
    if metadata.long_description:
        long_desc = rfc822_escape(metadata.get_long_description())
        print >>f, "Description:", long_desc
    keywords = metadata.get_keywords()
    if keywords:
        print >>f, "Keywords:", ", ".join(keywords)
    for platform in metadata.get_platforms():
        print >>f, "Platform:", platform
    for classifier in metadata.get_classifiers():
        print >>f, "Classifier:", classifier


def dumps(metadata):
    """Return package metadata serialized in PKG-INFO format."""
    sio = StringIO()
    dump(metadata, sio)
    return sio.getvalue()


def load(f, versioninfo=False, metadata=None):
    """Parse a PKG-INFO file and return a DistributionMetadata instance.

    Unsupported metadata formats cause a ValueError to be raised.
    """
    parser = Parser()
    msg = parser.parse(f, headersonly=True)
    return _loadmsg(msg, versioninfo, metadata)


def loads(text, versioninfo=False, metadata=None):
    """Parse PKG-INFO source text and return a DistributionMetadata instance.

    Unsupported metadata formats cause a ValueError to be raised.
    """
    parser = Parser()
    msg = parser.parsestr(text, headersonly=True)
    return _loadmsg(msg, versioninfo, metadata)


def _loadmsg(msg, versioninfo, metadata=None):
    if metadata is None:
        metadata = DistributionMetadata()

    if versioninfo:
        metadata.version = _get_single_header(msg, "Version")
    metadata.download_url = _get_single_header(msg, "Download-URL")
    metadata.name = _get_single_header(msg, "Name")
    metadata.author = _get_single_header(msg, "Author")
    metadata.author_email = _get_single_header(msg, "Author-email")
    metadata.maintainer = _get_single_header(msg, "Maintainer")
    metadata.maintainer_email = _get_single_header(msg, "Maintainer-email")
    metadata.url = _get_single_header(msg, "Home-page")
    metadata.license = _get_single_header(msg, "License")
    metadata.description = _get_single_header(msg, "Summary")
    metadata.long_description = _get_single_header(msg, "Description")

    keywords = _get_single_header(msg, "Keywords", "")
    keywords = [s.strip() for s in keywords.split(",") if s.strip()]
    metadata.keywords = keywords or None

    platforms = msg.get_all("Platform")
    if platforms:
        metadata.platforms = platforms

    classifiers = msg.get_all("Classifier")
    if classifiers:
        metadata.classifiers = classifiers

    return metadata


def _get_single_header(msg, name, default=None):
    """Return the value for a header that only occurs once in the input.

    If the header occurs more than once, ValueError is raised.
    """
    headers = msg.get_all(name)
    if headers and len(headers) > 1:
        raise ValueError("header %r can only be given once" % name)
    if headers:
        return headers[0]
    else:
        return default

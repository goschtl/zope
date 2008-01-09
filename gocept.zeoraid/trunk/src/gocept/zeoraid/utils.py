# vim:fileencoding=utf-8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Utilities."""

import logging
logger = logging.getLogger('gocept.zeoraid')


def guess_zodb_version():
    # Determine the version of ZODB used. Unfortunately ZODB doesn't have a
    # reliable version number accessible, so we need to do some guesstimation:

    # If there are no versions, we have a ZODB 3.9 (or later)
    import ZODB.DemoStorage
    if not hasattr(ZODB.DemoStorage.DemoStorage, 'supportsVersions'):
        return '3.9+'

    # If there are blobs, we have a ZODB 3.8
    try:
        import ZODB.blob
    except ImportError:
        pass
    else:
        return '3.8'

    # if ... we have a ZODB 3.7

    # if ... we have a ZODB 3.6

    # if ... we have a ZODB < 3.6 (unsupported)

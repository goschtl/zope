##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Filesystem-specific interfaces

$Id$
"""

from Interface import Interface


class FSReadError (Exception):
    """Unable to read data"""

class FSWriteError (Exception):
    """Unable to write data"""


class IFSReader (Interface):
    """Filesystem reader that supports annotations.
    """

    def get_subpath(oid):
        """Returns the tuple path for an oid, relative to the base.
        """

    def get_path(oid):
        """Returns the filesystem path for an oid.
        """

    def read_node_type(oid):
        """Reads the node type of a filesystem node.
        """

    def read_data(oid, allow_missing=0, as_text=0):
        """Reads the main data stream from a file.

        If the allow_missing flag is specified, this method returns
        None if no such file is found.  If as_text is true, the file
        is read in text mode.
        """

    def read_directory(oid, allow_missing=0):
        """Reads the contents of a directory.

        Returns a list of (object_name, child_oid).  The child_oid is
        None for objects not seen before.  The application should
        assign unique OIDs to the newly found children, then tell this
        object about the assignments through the assignNew() method.

        If the allow_missing flag is specified, this method returns
        None if no such directory is found.
        """

    def read_annotation(oid, name, default=None):
        """Reads a text-based annotation for a file.
        """

    def read_object_name(oid):
        """Gets the canonical name for an object.

        Note that this only makes sense when objects can have only one
        parent.
        """

    def assign_existing(oid, children):
        """Assigns OIDs to previously existing objects on the filesystem.

        See read_directory().  children is a list of (object_name, child_oid).
        """

    def read_extension(oid):
        """Returns the filename extension for a file.
        """

    def read_mod_time(oid, default=0):
        """Returns the last-modified time of a file.
        """

    def get_sources(oid):
        """Returns source information for an oid.

        The source information is a mapping that maps
        (source_repository, path) to a state object.  The contents of
        path and state are specific to a source repository.  The
        source repository (an ISourceRepository) may be polled
        periodically to freshen the state of objects in caches.
        """


class IFSWriter (Interface):
    """Filesystem writer that supports annotations.
    """

    def write_node_type(oid, data):
        """Writes the node type for a filesystem node.

        'd' (directory) and 'f' (file) are supported.
        """

    def write_data(oid, data, as_text=0):
        """Writes string data to a filesystem node.

        If 'as_text' is true, the file is written in text mode.
        """

    def write_directory(oid, data):
        """Writes data to a directory.

        'data' is a sequence of (object_name, child_oid).
        """

    def write_annotation(oid, name, data):
        """Writes a text-based annotation for a filesystem node.
        """

    def suggest_extension(oid, ext):
        """Suggests a filename extension for a filesystem node.

        The IFSConnection may use this information to store the file
        with an automatically appended filename extension.
        """

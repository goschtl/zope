##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Interfaces for the zope.httpform package.

$Id: $
"""

from zope.interface import Interface
from zope.interface import Attribute
from zope.interface.common.mapping import IExtendedReadMapping


class IFormParser(Interface):
    """Parses a form and holds the result."""

    def parse():
        """Parse the form data and return it as a mapping.

        Before parsing the form data, this method verifies the
        WSGI/CGI environment contains form data.  If it does not,
        this method returns an empty mapping.

        Returns the mapping of form data.
        """

    form = Attribute("form",
        """Mapping containing the parsed form data""")

    action = Attribute("action",
        """The :method or :action specified in the form data.

        Defaults to None.
        """)

class IFormRecord(IExtendedReadMapping):
    """A record parsed from a form.

    The form parser produces IFormRecord objects when forms contain
    :record values, such as this query string::

      point.x:int:record=10&point.y:int:record=20

    The record data can be retrieved through either item or attribute
    access.  Record attributes must not start with an underscore
    and must not match dictionary method names such as 'keys'.
    """

class IFileUpload(Interface):
    """Holds an uploaded file.

    Objects providing IFileUpload also have the standard file
    methods (read(), close(), etc.) so they can be used as normal files.
    """

    headers = Attribute("headers",
        """An rfc822.Message containing the file upload headers""")

    filename = Attribute("filename",
        """The name of the uploaded file, in Unicode""")

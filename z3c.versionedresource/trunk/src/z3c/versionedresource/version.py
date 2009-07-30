##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""Version Manager Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import subprocess
import zope.interface
from zope.schema.fieldproperty import FieldProperty
from z3c.versionedresource import interfaces


class VersionManager(object):
    zope.interface.implements(interfaces.IVersionManager)

    version = FieldProperty(interfaces.IVersionManager['version'])

    def __init__(self, version):
        self.version = version

    def __repr__(self):
        return '<%s %r>' %(self.__class__.__name__, self.version)

class SVNVersionManager(VersionManager):
    zope.interface.implements(interfaces.IVersionManager)

    COMMAND = 'svnversion -n %s'

    def __init__(self, path):
        process = subprocess.Popen(
            [self.COMMAND %path],
            shell=True, close_fds=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        status = process.wait()
        if status != 0:
            print process.stderr.read()
        self.version = 'r' + process.stdout.read()

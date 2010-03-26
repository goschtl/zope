##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""Generate a ``latest-versions.cfg`` file from the controlled list of
packages.

This file can

Usage: upload file-spec1, [file-spec2, ...] dest-location

* ``file-spec[N]``

  This argument specifies which file to upload. The file specification has the
  following syntax: ``<local-file-path> [ = <remote-file-name>]``

  The local file path is the path to the file. Optionally you can specify the
  name under which the file will be known remotely.

* ``dest-location``

  The server name and path of the remote directory.
"""
import os, sys
from zope.kgs import kgs

DRY_RUN = False

def do(cmd):
    print cmd
    if not DRY_RUN:
        status = os.system(cmd)
        if status != 0:
            sys.exit(status)

def upload(fileSpecs, destination):
    """Upload files to the server."""
    for localPath, remoteName in fileSpecs:
        destinationPath = os.path.join(destination, remoteName)
        do('scp %s %s' %(localPath, destinationPath))

def getAllFileSpecs(files):
    fileSpecs = []
    for filePath, name in files:
        fileSpecs.append((filePath, name))
        if not filePath.endswith('controlled-packages.cfg'):
            continue
        set = kgs.KGS(filePath)
        if set.changelog:
            fileSpecs.insert(0, (
                set.changelog, os.path.split(set.changelog)[-1]))
        if set.announcement:
            fileSpecs.insert(0, (
                set.announcement, os.path.split(set.announcement)[-1]))
        for filePath in set.files:
            fileSpecs.insert(0, (filePath, os.path.split(filePath)[-1]))
    return fileSpecs


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    if len(args) < 2:
        print __doc__
        sys.exit(1)

    destination = args[-1]

    fileSpecs = []
    for spec in args[:-1]:
        if '=' in spec:
            fileSpecs.append(
                tuple([part.strip() for part in spec.split('=')]))
        else:
            spec = spec.strip()
            fileSpecs.append(
                (spec, os.path.split(spec)[-1]))
    upload(getAllFileSpecs(fileSpecs), destination)

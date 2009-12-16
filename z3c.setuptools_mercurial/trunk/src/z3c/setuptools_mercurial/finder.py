##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""Find all files checked into a mercurial repository.

$Id$
"""
import logging
import os.path
import subprocess

def find_files(dirname="."):
    """Find all files checked into a mercurial repository."""
    dirname = os.path.abspath(dirname)
    try:
        # List all files of the repository as absolute paths.
        proc = subprocess.Popen(['hg', 'locate', '-f'],
                                stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                cwd=dirname)
        stdout, stderr = proc.communicate()
    except Exception, err:
        logging.error(str(err))
        # If anything happens, return an empty list.
        return []
    # The process finished, but returned an error code.
    if proc.returncode != 0:
        logging.error(stderr+ ' (code %i)' %proc.returncode)
        return []
    # The process finished successfully, so let's use the result. Only select
    # those files that really belong to the passed in directory.
    return [path.replace(dirname, '.')
            for path in stdout.splitlines()
            if path.startswith(dirname)]

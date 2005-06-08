##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Utilities to help log running an external command."""

import os
import sys

from zpkgsetup import loggingapi as logging


def report_command(cmd):
    """Report that we're running an external process.

    :param cmd:  The command line we're going to run.

    """
    logger = _get_logger()
    #
    # XXX Using two log entries isn't really the right way to do this,
    # but makes things easier to debug for now.  Not sure how well the
    # log formats deal with multi-line messages, so this suffice.
    #
    logger.debug("running: %s", cmd)
    logger.debug("  (cwd = %s)", os.getcwd())


def report_exit_code(rc):
    """Report the exit code for an external process.

    :param rc:  The return code of the process.

    """
    logger = _get_logger()
    logger.debug("exit code: %s", rc)


def _get_logger():
    """Return the logger to report with.

    :rtype: logging.Logger

    """
    f = sys._getframe(2)
    name = f.f_globals.get("__name__", "<unknown>")
    return logging.getLogger(name)

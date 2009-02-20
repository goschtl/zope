##############################################################################
#
# Copyright (c) Zope Corporation and Contributors.
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

import logging

def level(connection, logger, level=None):
    """Get or set a log level

    Provide a logger name to get the current level.
    Provide a logger name and a ner level to set the level.
    """

    if logger == '.':
        logger = logging.getLogger()
    else:
        logger = logging.getLogger(logger)

    if level is None:
        level = logger.getEffectiveLevel()
        connection.write(logging.getLevelName(level)+'\n')
        return

    try:
        level = int(level)
    except ValueError:
        v = getattr(logging, level, None)
        if not isinstance(v, int) or v < 0:
            raise ValueError("Invalid log level", level)
        level = v

    logger.setLevel(level)
    

##############################################################################
#
# Copyright (c) 2009 Fabio Tranchitella <fabio@tranchitella.it>
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

"""
$Id$
"""

import bobo


class Application(bobo.Application):
    """Create a WSGI application based on bobo"""

    def __init__(self, DEFAULT=None, **config):
        # add the z3c.bobopublisher publication subroute
        config['bobo_resources'] = ('z3c.bobopublisher.publication' + \
            '\n' + config.get('bobo_resources', '')).rstrip()
        # call the original __init__ method
        return bobo.Application.__init__(self, DEFAULT, **config)

##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""

$Id: PublisherFTPTask.py,v 1.2 2002/06/10 23:29:35 jim Exp $
"""

from FTPTask import FTPTask
from Zope.Publisher.Publish import publish


class PublisherFTPTask(FTPTask):
    """ """

    __implements__ = FTPTask.__implements__


    def execute(self):
        """ """
        server = self.channel.server
        env = self.create_environment()
        instream = self.request_data.getBodyStream()

        request = server.request_factory(instream, self, env)
        publish(request)


    def create_environment(self):
        request_data = self.request_data
        channel = self.channel
        server = channel.server

        # This should probably change to reflect calling the FileSystem
        # methods
        env = {'command': request_data.command
               'args': request_data.args
               }


        return env

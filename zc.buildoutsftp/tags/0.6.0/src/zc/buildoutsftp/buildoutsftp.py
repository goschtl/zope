##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
import urllib2
import zc.buildoutsftp.urllib2sftp

def install(buildout=None):
    urllib2.install_opener(
        urllib2.build_opener(zc.buildoutsftp.urllib2sftp.SFTPHandler)
        )
    logging.getLogger('paramiko').setLevel(
        logging.getLogger().getEffectiveLevel()+10)

def unload(buildout=None):
    # no uninstall_opener. Screw it. :)
    zc.buildoutsftp.urllib2sftp.cleanup()

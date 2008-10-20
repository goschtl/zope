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
import glob

import zope.interface
import zope.configuration.config
import zope.schema
    
def exclude(_context, file=None, package=None, files=None):
    """Exclude a zcml file
    """

    if files:
        if file:
            raise ValueError("Must specify only one of file or files")
    elif not file:
        file = 'configure.zcml'


    context = zope.configuration.config.GroupingContextDecorator(_context)
    if package is not None:
        context.package = package
        context.basepath = None

    if files:
        paths = glob.glob(context.path(files))
        paths = zip([path.lower() for path in paths], paths)
        paths.sort()
        paths = [path for (l, path) in paths]
    else:
        paths = [context.path(file)]

    for path in paths:
        # processFile returns a boolean indicating if the file has been
        # processed or not, it *also* marks the file as having been processed,
        # here the side effect is used to keep the given file from being
        # processed in the future
        context.processFile(path)

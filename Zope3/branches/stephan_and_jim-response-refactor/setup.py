#############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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

import os
import site
import sys

here = os.path.dirname(os.path.abspath(__file__))
buildsupport = os.path.join(here, "buildsupport")

sys.path.insert(0, buildsupport)
# Process *.pth files from buildsupport/:
site.addsitedir(buildsupport)

import zpkgsetup.package
import zpkgsetup.publication
import zpkgsetup.setup


context = zpkgsetup.setup.SetupContext(
    "Zope", "3.1.0a42", __file__)

context.load_metadata(
    os.path.join(here, "releases", "Zope",
                 zpkgsetup.publication.PUBLICATION_CONF))

context.walk_packages("src")
context.setup()

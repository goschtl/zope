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

import zpkgsetup.setup


here = os.path.dirname(os.path.abspath(__file__))

context = zpkgsetup.setup.SetupContext(
    "Zope", "3.1.0a42", __file__)

context.load_metadata(
    os.path.join(here, "releases", "Zope", "PUBLICATION.cfg"))

for root, dirs, files in os.walk("src"):
    for d in dirs[:]:
        # drop sub-directories that are not Python packages:
        initfn = os.path.join(root, d, "__init__.py")
        if not os.path.isfile(initfn):
            dirs.remove(d)
    if "SETUP.cfg" in files:
        # scan this directory as a package:
        pkgname = root[4:].replace(os.path.sep, ".")
        local_full_path = os.path.join(here, root)
        relative_path = root.replace(os.path.sep, "/")
        context.scan(pkgname, local_full_path, relative_path)

context.setup()

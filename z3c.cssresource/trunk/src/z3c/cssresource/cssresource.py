##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
"""CSS Resource

$Id$
"""
import re

from zope.app.publisher.fileresource import File
from zope.app.publisher.browser.fileresource import FileResource

# Allows matches of the form: /* ZOPE-COMMAND: "ORIGINAL" "FINAL" */
directive_regex = r' */\* *%s: *"([^ "]*)" *"([^ "]*)" *\*/'
global_replace = re.compile(directive_regex %'zope-global-replace')

class CSSFileResource(FileResource):

    def process(self, data):
        # Find all directives
        directives = re.compile(
            directive_regex %'zope-global-replace').findall(data)
        # Remove directives from file
        data = re.compile(
            (directive_regex+'\n') %'zope-global-replace').sub('', data)
        # Now execute directives
        for orig, final in directives:
            data = data.replace(orig, final)
        return data

    def GET(self):
        data = super(CSSFileResource, self).GET()
        return self.process(data)


class CSSFileResourceFactory(object):

    def __init__(self, path, checker, name):
        self.__file = File(path, name)
        self.__checker = checker
        self.__name = name

    def __call__(self, request):
        resource = CSSFileResource(self.__file, request)
        resource.__Security_checker__ = self.__checker
        resource.__name__ = self.__name
        return resource

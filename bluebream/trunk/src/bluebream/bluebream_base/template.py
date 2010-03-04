##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
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
import sys
from paste.script import templates
from paste.script.templates import var


class BlueBream(templates.Template):

    _template_dir = 'project_template'
    summary = "A BlueBream project, base template"

    vars = [
        var('namespace_package', 'Namespace package name'),
        var('main_package',
            'Main package name (under the namespace)',
            default='main'),
        var('interpreter',
            'Name of custom Python interpreter',
            default='breampy'),
        var('version', 'Version (like 0.1)', default='0.1'),
        var('description', 'One-line description of the package'),
        var('long_description', 'Multi-line description (in reST)'),
        var('keywords', 'Space-separated keywords/tags'),
        var('author', 'Author name'),
        var('author_email', 'Author email'),
        var('url', 'URL of homepage'),
        var('license_name', 'License name'),
        var('zip_safe',
            'True/False: if the package can be distributed as a .zip file',
            default=False),
        ]

    def check_vars(self, vars, cmd):

        if vars['package'] in ('bluebream', 'bream', 'zope'):
            print
            print "Error: The chosen project name results in an invalid " \
                "package name: %s." % vars['package']
            print "Please choose a different project name."
            sys.exit(1)

        for var in self.vars:
            if var.name == 'namespace_package':
                var.default = vars['package']

        vars = templates.Template.check_vars(self, vars, cmd)

        return vars

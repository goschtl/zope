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
import re, os, sys
import pkg_resources
from paste.script import templates
from paste.script.templates import var


class BlueBream(templates.Template):

    _template_dir = 'project_template'
    summary = "A BlueBream project, base template"

    vars = [
        var('package',
            'Main Python package (with namespace if any)'),
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

    def check_name(self, name):
        """Disallow certain package names
        """
        if name in ('bluebream', 'bream', 'zope'):
            print
            print "Error: The chosen project name results in an invalid " \
                "package name: %s." % name
            print "Please choose a different project name."
            sys.exit(1)

    def check_vars(self, vars, cmd):
        """This method checks and cleans the variables
        passed on the command line
        """
        # check once just after the project name choice
        pkg_name = re.sub('[^A-Za-z0-9.]+', '_', vars['project']).lower()
        self.check_name(pkg_name)

        # remove Paste chosen value for the package name and suggest a new one
        del vars['package']
        for var in self.vars:
            if var.name == 'package':
                var.default = pkg_name

        # ask the remaining questions
        vars = templates.Template.check_vars(self, vars, cmd)
        # check again since we could chose anything
        self.check_name(vars['package'])
        return vars

    def pre(self, command, output_dir, vars):
        """Detect namespaces in the project name
        """
        if not command.options.verbose:
            command.verbose = 0
        self.ns_split = vars['package'].split('.')
        vars['package'] = self.ns_split[-1]
        vars['namespace_packages'] = list(reversed([
                    vars['package'].rsplit('.', i)[0]
                    for i in range(1,len(self.ns_split))]))
        vars['ns_prefix'] = '.'.join(self.ns_split[:-1]) + '.'
        if len(self.ns_split) == 1:
            vars['ns_prefix'] = ''


    def post(self, command, output_dir, vars):
        """Add namespace packages and move the main package to the last level
        """
        # do nothing if there is no namespace
        if len(self.ns_split) == 1:
            return

        # create the intermediate namespace packages
        target_dir = os.path.join(output_dir, 'src',
                                  os.path.join(*self.ns_split[:-1]))

        os.makedirs(target_dir)

        # create each __init__.py with namespace declaration
        ns_decl = "__import__('pkg_resources').declare_namespace(__name__)"
        for i, namespace_package in enumerate(self.ns_split[:-1]):
            init_file = os.path.join(output_dir, 'src',
                                     os.path.join(*self.ns_split[:i+1]),
                                     '__init__.py')
            open(init_file, 'w').write(ns_decl)

        # move the main package to the last namespace
        package_dir = os.path.join(output_dir, 'src', vars['package'])
        os.rename(package_dir,
                  os.path.join(target_dir, os.path.basename(package_dir,)))



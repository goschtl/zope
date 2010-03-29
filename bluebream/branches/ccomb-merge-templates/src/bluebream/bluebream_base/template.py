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
import re, os, sys, shutil
import pkg_resources
from paste.script import templates
from paste.script.templates import var


class BlueBream(templates.Template):

    _template_dir = 'project_template'
    summary = "A BlueBream project, base template"

    vars = [
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

        # detect namespaces in the project name
        vars['package'] = re.sub('[^A-Za-z0-9.]+', '_', vars['project']).lower()
        vars['main_package'] = vars['package'].split('.')[-1]
        self.ns_split = vars['project'].split('.')
        vars['namespace_packages'] = [
                    vars['package'].rsplit('.', i)[0]
                    for i in range(1,len(self.ns_split))]
        vars['ns_prefix'] = '.'.join(self.ns_split[:-1])
        if len(self.ns_split) == 0:
            vars['ns_prefix'] = ''

        return templates.Template.check_vars(self, vars, cmd)

    def write_files(self, command, output_dir, vars):
        "Add namespace packages and move the main package to the last level"
        templates.Template.write_files(self, command, output_dir, vars)

        if len(self.ns_split) > 1:
            print 'Namespace package detected!'
            target_dir = os.path.join(output_dir, 'src',
                                      os.path.join(*self.ns_split[:-1]))

            print 'Creating directory %s' % target_dir
            os.makedirs(target_dir)

            ns_decl = "__import__('pkg_resources').declare_namespace(__name__)"
            for i, namespace_package in enumerate(self.ns_split[:-1]):
                init_file = os.path.join(output_dir, 'src',
                                         os.path.join(*self.ns_split[:i+1]),
                                         '__init__.py')
                print 'Creating namespace-enabled %s' % init_file
                open(init_file, 'w').write(ns_decl)
            main_package_dir = os.path.join(output_dir,
                                            'src',
                                            vars['main_package'])
            print 'Moving %s to %s' % (main_package_dir, target_dir)
            shutil.move(main_package_dir, target_dir)




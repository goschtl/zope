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

# without namespace package, so really worry about this for newcomers
ILLEGAL_NAMES = ('zope', 'z3c', 'zc', 'grokcore', 'megrok', 'bluebream',
                 'bream')

# we not use variable `package' but only `project' and we like
# straightforward behavior

class BlueBream(templates.Template):

    _template_dir = 'project_template'
    summary = "A BlueBream project, simple template"

    def check_vars(self, vars, cmd):
        if vars['project'] in ILLEGAL_NAMES:
            print "\nError: The chosen project name results in an invalid " \
                "package name: %s." % vars['project']
            print "Please choose a different project name."
            sys.exit(1)

        vars = templates.Template.check_vars(self, vars, cmd)

        return vars

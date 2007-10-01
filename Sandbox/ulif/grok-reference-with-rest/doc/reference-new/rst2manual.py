#!/usr/bin/python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
A minimal front end to the Docutils Publisher, producing LaTeX.
"""

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass


from docutils.core import publish_cmdline, default_description
import latex_manual
import latex_manual.roles
import latex_manual.directives

class Environment(object):
    currmodlue = None

env = Environment()

#import latex_manual.addnodes

#env.currmodule = ''

description = ('Generates LaTeX documents from standalone reStructuredText '
               'sources.  ' + default_description)

publish_cmdline(writer_name='latex_manual', description=description)





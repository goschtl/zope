##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""Generate a XXX/TODO report.
"""

import cc.buildout_reports

import os
import stat
import logging
import subprocess
import zc.buildout

class XxxReport:
    """Generate an HTML XXX/TODO comment report for the project.  Supports
    the following configuration parameters:

    * pattern: the pattern to scan for; if not specified, defaults to
        (XXX|TODO)
        
    * report_file: the file to save the report to; if not specified, defaults
        to XXXreport.html, stored in the buildout directory.  If specified
        as a relative path, it is interpreted as relative to the buildout
        directory.
        
    """
    
    def __init__(self, buildout, name, options):

        self.buildout, self.name, self.options = buildout, name, options
        
        # perform sanity checking on parameters
        
        if 'pattern' not in options:
            # no pattern to scan for provided; default to XXX|TODO
            options['pattern'] = '?(XXX|TODO)'
            
            logging.getLogger(name).info(
                "No comment pattern for XXX report specified; using %s",
                options['pattern'])

        if 'report_file' not in options:
            # no output file provided; default to 'XXXreport.html'
            options['report_file'] = os.path.join(
                buildout['buildout']['directory'], 'XXXreport.html')
            logging.getLogger(name).info(
                "No output file for XXX report specified; using %s",
                options['report_file'])
        else:
            # make sure the path is absolute
            options['report_file'] = os.path.abspath(options['report_file'])


        # determine the name of our script
        self.script_name = os.path.join(
            os.path.dirname(cc.buildout_reports.__file__),
            'xxx_report.sh')

        # make sure it's executable
        if not(os.access(self.script_name, os.X_OK)):
            # attempt to chmod it... sigh...
            os.chmod(self.script_name,
                     stat.S_IRUSR|stat.S_IWUSR|stat.S_IXUSR|
                     stat.S_IXGRP|stat.S_IXOTH)

    def install(self):
        """Generate the XXX report for this project."""

        subprocess.call([self.script_name,
                         self.buildout['buildout']['directory'],
                         self.options['report_file'],
                         self.options['pattern']
                         ])
                
        return [self.options['report_file']]

    update = install

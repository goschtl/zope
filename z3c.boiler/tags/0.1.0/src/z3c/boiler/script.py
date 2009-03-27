##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Command Line Interface

$Id$
"""
import logging
import optparse
import os
import sys
from z3c.feature.core import xml, template
from z3c.feature.core.interfaces import IFileBasedTemplateProvider
from z3c.feature.core.interfaces import MissingFeatureDependencyError
from z3c.builder.core import base, interfaces
from z3c.boiler import interactive

parser = optparse.OptionParser()
parser.add_option(
    "-i", "--input-file", action="store",
    dest="inputFile", metavar="FILE",
    help="The file containing the XML definition of the project.")

parser.add_option(
    "-t", "--template", action="store",
    dest="template",
    help="A project template.  Use --list to see available templates")

parser.add_option(
    "-l", "--list", action="store_true",
    dest="listTemplates",
    help="Show a list of available templates for use with --template")

parser.add_option(
    "-k", "--interactive", action="store_true",
    dest="interactive", default=False,
    help=("When specified, runs in interactive mode "
          "prompting you to enter missing values."))

parser.add_option(
    "-o","--output-dir", action="store",
    dest="outputDirectory", metavar="DIR",
    default=u".",
    help="The directory where project files should be generated.")

parser.add_option(
    "-q","--quiet", action="store_true",
    dest="quiet", default=False,
    help="When specified, no messages are displayed.")

parser.add_option(
    "-v","--verbose", action="store_true",
    dest="verbose", default=False,
    help="When specified, debug information is created.")


parser.add_option(
    "-f","--force", action="store_true",
    dest="force",
    help=("Force the package to be generated "
          "even overwriting any existing files."))


def main(args=None):
    # Make sure we get the arguments.
    if args is None:
        args = sys.argv[1:]
    if not args:
        args = ['-h']

    # Set up logger handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(base.formatter)
    base.logger.addHandler(handler)

    # Parse arguments
    options, args = parser.parse_args(args)

    if options.listTemplates:
        print "Available Templates:"
        print
        temps = [(name, temp) for name, temp in template.getTemplateList().items()
                 if IFileBasedTemplateProvider.providedBy(temp)]
        nameSize = max([len(name) for name, temp in temps])
        for name, temp in temps:
            nameLine = '  %s' % name
            nameLine += ' '*(nameSize-len(name))
            nameLine += ' "%s"' % temp.title
            print nameLine
            print nameSize*' '+'     '+temp.description.strip().replace('\n','\n    ')
        sys.exit(0)

    if not options.inputFile and not options.template:
        print "You must specify an input file or template"
        args = ['-h']
        parser.parse_args(args)
    elif not options.inputFile:
        try:
            inputFile = template.getTemplate(options.template).filename
        except KeyError:
            print "Could not find the template \"%s\"." % options.template
            print "Use --list to see available templates."
            sys.exit(1)
    else:
        inputFile = options.inputFile

    base.logger.setLevel(logging.INFO)
    if options.verbose:
        base.logger.setLevel(logging.DEBUG)
    if options.quiet:
        base.logger.setLevel(logging.FATAL)

    status = 0
    # Parse the project XML file into builder components.
    if options.interactive:
        try:
            builder = interactive.xmlToProject(open(inputFile, 'r'))
        except KeyboardInterrupt:
            print "\nquitting"
            sys.exit(status)
    else:
        try:
            builder = xml.xmlToProject(open(inputFile, 'r'))
        except MissingFeatureDependencyError, e:
            base.logger.fatal("An error occured:\n  %r" % e)
            sys.exit(1)

    # Write the project using the builders.
    try:
        builder.update()
        builder.write(options.outputDirectory, options.force)
    except interfaces.FileExistsException, e:
        base.logger.fatal("Failed building package because file %s "
                          "already exists.  Use --force to overwrite "
                          "it." % e.filename)
        status = 1
    else:
        base.logger.info("Build finished")

    # Remove the handler again.
    base.logger.removeHandler(handler)

    # Exit cleanly.
    sys.exit(status)

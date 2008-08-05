##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
"""Resource List

$Id$
"""
__docformat__ = 'restructuredtext'
import optparse
import os
import zope.component
import zope.interface
from zope.configuration import xmlconfig
from zope.publisher.browser import TestRequest
from z3c.versionedresource import interfaces, resource


def getAllResources(options):
    # Run the configuration
    context = xmlconfig.file(options.zcml)
    # Get the layer interface
    moduleName, layerName = options.layer.rsplit('.', 1)
    module = __import__(moduleName, {}, {}, [1])
    layer = getattr(module, layerName)
    # Now we create a test request with that layer and our custom base URL.
    request = TestRequest(environ={'SERVER_URL': options.url})
    zope.interface.alsoProvides(request, layer)
    # Next we look up all the resources
    resources = zope.component.getAdapters(
        (request,), interfaces.IVersionedResource)
    paths = []
    for name, res in resources:
        # For file-based resources, just report their URL.
        if not isinstance(res, resource.DirectoryResource):
            paths.append(res())
        # For directory resources, we want to walk the tree.
        baseURL = res()
        path = res.context.path
        for root, dirs, files in os.walk(path):
            if '.svn' in dirs:
                dirs.remove('.svn')
            relativePath = root.replace(path, '')
            for file in files:
                paths.append(baseURL + relativePath + '/' + file)
    return paths

###############################################################################
# Command-line UI

parser = optparse.OptionParser("%prog [options] ROOT-ZCML-FILE")

config = optparse.OptionGroup(
    parser, "Configuration", "Configuration of lookup and reporting parameters.")

config.add_option(
    '--url', '-u', action="store", dest='url',
    help="""The base URL that is used to produce the resource URLs.""")

config.add_option(
    '--layer', '-l', action="store", dest='layer',
    default='zope.interface.Interface',
    help="""The layer for which to lookup the resources.""")

parser.add_option_group(config)

# Default setup
default_setup_args = []

def merge_options(options, defaults):
    odict = options.__dict__
    for name, value in defaults.__dict__.items():
        if (value is not None) and (odict[name] is None):
            odict[name] = value

def get_options(args=None, defaults=None):

    default_setup, _ = parser.parse_args(default_setup_args)
    assert not _
    if defaults:
        defaults, _ = parser.parse_args(defaults)
        assert not _
        merge_options(defaults, default_setup)
    else:
        defaults = default_setup

    if args is None:
        args = sys.argv
    original_args = args
    options, positional = parser.parse_args(args)
    merge_options(options, defaults)
    options.original_args = original_args

    if not positional or len(positional) < 1:
        parser.error("No target user and/or packages specified.")
    options.zcml = positional[0]

    return options

# Command-line UI
###############################################################################

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    options = get_options(args)
    options.action = 'Add'
    resources = getAllResources(options)
    print '\n'.join(resources)

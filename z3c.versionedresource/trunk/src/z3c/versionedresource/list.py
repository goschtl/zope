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
import gzip
import optparse
import os
import sys
import zope.component
import zope.interface
from zope.configuration import xmlconfig
from zope.publisher.browser import TestRequest
from z3c.versionedresource import interfaces, resource
from z3c.versionedresource.resource import DirectoryResource

EXCLUDED_NAMES = ('.svn',)

def removeExcludedNames(list):
    for name in EXCLUDED_NAMES:
        if name in list:
            list.remove(name)

def getResources(layerPaths, url='http://localhost/'):
    resources = ()
    for layerPath in layerPaths:
        # Get the layer interface
        moduleName, layerName = layerPath.rsplit('.', 1)
        module = __import__(moduleName, {}, {}, ['None'])
        layer = getattr(module, layerName)
        # Now we create a test request with that layer and our custom base URL.
        request = TestRequest(environ={'SERVER_URL': url})
        zope.interface.alsoProvides(request, layer)
        # Next we look up all the resources
        resources += tuple(
            zope.component.getAdapters(
                (request,), interfaces.IVersionedResource))
    return resources

def getResourceUrls(resources):
    paths = []
    for name, res in resources:
        # For file-based resources, just report their URL.
        if not isinstance(res, DirectoryResource):
            # Avoid duplicate paths
            if res() not in paths:
                paths.append(res())
        # For directory resources, we want to walk the tree.
        baseURL = res()
        path = res.context.path
        for root, dirs, files in os.walk(path):
            # Ignore unwanted names.
            removeExcludedNames(dirs)
            removeExcludedNames(files)
            # Produce a path for the resource
            relativePath = root.replace(path, '')
            for file in files:
                fullPath = baseURL + relativePath + '/' + file
                # Avoid duplicate paths
                if fullPath not in paths:
                    paths.append(fullPath)
    return paths

def storeResource(dir, name, resource, zip=False):
    outputPath = os.path.join(dir, name)
    # For directory resources, we create the directory and walk through the
    # children.
    if isinstance(resource, DirectoryResource):
        if not os.path.exists(outputPath):
            os.mkdir(outputPath)
        for name in [name for name in os.listdir(resource.context.path)
                     if name not in EXCLUDED_NAMES]:
            subResource = resource.get(name, None)
            if subResource is not None:
                storeResource(outputPath, name, subResource, zip)
    # For file-based resources, get the path, load it and store it at the new
    # location.
    else:
        inFile = open(resource.context.path, 'r')
        openFile = open
        if zip:
            openFile = gzip.open
        outFile = openFile(outputPath, 'w')
        outFile.write(inFile.read())
        inFile.close()
        outFile.close()

def produceResources(options):
    # Run the configuration
    context = xmlconfig.file(options.zcml)
    # Get resource list
    resources = getResources(options.layers, options.url)
    # If we only want to list the paths
    if options.listOnly:
        paths = getResourceUrls(resources)
        print '\n'.join(paths)
        return
    # Now we can produce the version directory with all resources in it
    version = zope.component.getUtility(interfaces.IVersionManager).version
    outputdir = os.path.join(options.dir, version)
    if not os.path.exists(outputdir):
        os.mkdir(outputdir)
    for name, resource in resources:
        storeResource(outputdir, name, resource, options.zip)
    print outputdir

###############################################################################
# Command-line UI

parser = optparse.OptionParser("%prog [options] ROOT-ZCML-FILE")

config = optparse.OptionGroup(
    parser, "Configuration", "Configuration of lookup and reporting parameters.")

config.add_option(
    '--layer', '-l', action="append", dest='layers',
    help="""The layer for which to lookup the resources.""")

config.add_option(
    '--zip', '-z', action="store_true", dest='zip', default=False,
    help="""When set, resources are stored in GZIP format.""")

config.add_option(
    '--output-dir', '-d', action="store", dest='dir',
    default=os.path.abspath(os.curdir),
    help="""The directory in which the resources will be stored.""")

parser.add_option_group(config)

list = optparse.OptionGroup(
    parser, "List", "Options for list only result.")

list.add_option(
    '--list-only', action="store_true", dest='listOnly', default=False,
    help="When specified causes no directory with the resources "
         "to be created.")

list.add_option(
    '--url', '-u', action="store", dest='url', default='http://localhost/',
    help="""The base URL that is used to produce the resource URLs.""")

parser.add_option_group(list)

def get_options(args=None):
    if args is None:
        args = sys.argv
    original_args = args
    options, positional = parser.parse_args(args)
    options.original_args = original_args

    if not positional or len(positional) < 1:
        parser.error("No target user and/or packages specified.")
    options.zcml = positional[0]

    return options

# Command-line UI
###############################################################################

def main(args=None):
    options = get_options(args)
    try:
        produceResources(options)
    except Exception, err:
        print err
        sys.exit(1)
    sys.exit(0)

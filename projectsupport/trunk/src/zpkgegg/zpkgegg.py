##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""
mksetup.py

Read zpkg style config files to generate a simple setup.py which can
be used to build an egg.
"""

import os
import shutil
import sys
import optparse
import subprocess
import fnmatch
import tempfile

import zpkgsetup.package

class EagerDict(object):
    """A dictionary which will _always_ return something for any key;
    if the key does not exist, an empty string is returned."""
    
    def __init__(self):
        self.__real = {}

    def __setitem__(self, key, value):
        self.__real[key] = value
        
    def __getitem__(self, key):
        if key in self.__real:
            return self.__real[key]
        else:
            return ''
        
def makeArgParser():
    """Create an OptionParser and configure it to work with mksetup.py"""
    
    parser = optparse.OptionParser(
        usage="mksetup.py [options] <source directory>")
    parser.add_option("-p", "--template", dest="project_template",
                      help="Directory containing the project template." )
    parser.add_option("-w", "--working", dest="workdir",
                      help="Working directory for project build out.")
    parser.add_option("-s", "--setup", dest="setup",
                      help="Template to use for generating setup.py.")
    parser.add_option("-v", "--version", dest="version",
                      help="Version of the package.")
    
    parser.add_option("-e", "--eggdir", dest="eggdir",
                      help="Directory to store eggs in.")
    parser.add_option("-t", "--tree", dest="tree_only",
                      action="store_true",
                      help="Only build the project tree.")
    parser.add_option("-n", "--nodelete", dest="delete_tree",
                      action="store_false",
                      help="Do not delete the source tree after building packages.")

    parser.set_defaults(project_template=None,
                        setup = os.path.join(os.path.dirname(__file__),
                                             "setup.template"),
                        eggdir = os.path.join(os.getcwd(),
                                              "eggs"),
                        workdir= None,
                        
                        version="1.0",
                        tree_only=False,
                        delete_tree=True,
                        )

    return parser

def fixup_opts(opts):
    """Takes an Options object containing the parsed arguments from the
    commmand-line and performs finalization."""

    if opts.project_template is None:
        # no project template was specified... try a handful of places
        # 1) a project-template/trunk directory in the pwd
        # 2) a project-template/trunk directory in the relative location
        #    it would exist in a projectsupport subversion checkout
        
        candidates = [os.path.join(os.getcwd(), "project-template", "trunk"),
                      os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                   "..", "..",
                                                   "project-template",
                                                   "trunk")),
                      ]

        for p in candidates:
            if os.path.exists(p):
                opts.project_template = p
                break

    if opts.workdir is None:
        # no working directory specified; generate a temp dir
        opts.workdir = os.path.join(tempfile.gettempdir(), "blarf")
            

def make_project_template(template, target):
    """Make sure the destination directory does not exist,
    and then duplicate the project template into it."""

    if os.path.exists(target):
        print "*** Output path (%s) exists. ***" % target
        sys.exit(2)
        
    # duplicate the template directory
    shutil.copytree(template, target)


def make_extension(pkg_name, ext_def):
    """Takes a ZConfig SectionValue and generates the Python code for
    declaring the Extension in setup.py."""

    def __src_path(source_file):
        # it's magic; don't fuck with it
        return 'os.path.join ("src",' + \
               ','.join(['"%s"' % n for n in pkg_name.split('.')]) + \
               ', "' + source_file + '")'
    
    return """Extension("%s.%s",\n[%s]\n),\n""" % (pkg_name, ext_def._name,
                                               ",".join([__src_path(n)
                                                   for n in ext_def.source])
                                               )

def read_zpkg_data(source_dir):
    """Read the zpkg configuration information from the source directory
    and return a dictionary to use in generating setup.py"""

    DEPENDENCIES_CFG = os.path.join(source_dir, 'DEPENDENCIES.cfg')
    PUBLICATION_CFG = os.path.join(source_dir, 'PUBLICATION.cfg')
    
    # create the default substitution dictionary
    subst_data = EagerDict()
    subst_data['dependencies'] = '[]'
    subst_data['extensions'] = []
    subst_data['Name'] = ".".join(source_dir.split(os.sep)[-2:])

    # read in the zpkg configuration files
    if os.path.exists(DEPENDENCIES_CFG):
        deps = [n.strip() for n in file(DEPENDENCIES_CFG, 'r').read().split()]
        subst_data['dependencies'] = str(deps)

    if os.path.exists(PUBLICATION_CFG):
        for line in file(PUBLICATION_CFG, 'r'):
            if not(line.strip()):
                continue

            key, value = line.split(':', 1)
            subst_data[key.strip()] = value.strip()

    # read the package extension configuration, if it exists
    if os.path.exists(os.path.join(source_dir, 'SETUP.cfg')):
        ext_info = zpkgsetup.package.read_package_info(source_dir)

        # XXX still need to handle headers appropriately (see zope.proxy)
        
        for e in ext_info.extensions:
            subst_data['extensions'].append(make_extension(subst_data['Name'], e))

    subst_data['extensions'] = ",".join(subst_data['extensions'])

    return subst_data

def copy_package(source_dir, target_dir):
    # copy the target files into the correct loction
    shutil.copytree(source_dir,
                    os.path.join(target_dir, "src", "zope",
                                 os.path.basename(source_dir))
                    )
    
    
def setup_py(template, output_fn, user_data):
    """Load the specified template, perform a string substitution and write
    the result out to [output_fn]."""
    
    # generate and write out setup.py
    file(output_fn, 'w').write(
        file(template, 'r').read() % user_data
        )

def copy_eggs(source_dir, dest_dir):
    """Copy anything that looks like a distutils build from source_dir
    to dest_dir."""

    source_files = os.listdir(source_dir)
    for fn in fnmatch.filter(source_files, "*.egg"):
        shutil.copyfile(os.path.join(source_dir, fn),
                        os.path.join(dest_dir, fn))

    for fn in fnmatch.filter(source_files, "*.tar.gz"):
        shutil.copyfile(os.path.join(source_dir, fn),
                        os.path.join(dest_dir, fn))

def main(args):
    # parse and validate arguments
    opts, args = makeArgParser().parse_args()
    fixup_opts(opts)
    
    if len(args) < 1:
        print "You must supply the source directory as an argument."
        sys.exit(1)

    # get the source directory
    source_dir = os.path.abspath(args[0])

    # create the project directory structure
    make_project_template(opts.project_template, opts.workdir)
    copy_package(source_dir, opts.workdir)
    
    # read the zpkg metadata
    proj_data = read_zpkg_data(source_dir)
    proj_data['version'] = opts.version

    # generate the setup.py
    setup_py(opts.setup, os.path.join(opts.workdir, 'setup.py'), proj_data)

    # see if we want to build eggs/sdists, or just leave the tree
    if not(opts.tree_only):
        # build the egg and sdist
        # sys.argv = ['setup.py', 'sdist']
        #sys.path.insert(0, os.path.abspath(opts.workdir))

        startdir = os.getcwd()
        
        os.chdir(opts.workdir)
        subprocess.call(["python", "setup.py", "sdist", "bdist_egg"])
        os.chdir(startdir)
        
        # copy the egg to the eggdir
        copy_eggs(os.path.join(opts.workdir, "dist"), opts.eggdir)
        
        # remove the tree
        if opts.delete_tree:
            shutil.rmtree(opts.workdir)
    
        
if __name__ == '__main__':
    main(sys.argv[1:])
    

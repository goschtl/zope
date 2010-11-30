# Copyright (c) 2010 Zope Foundation and Contributors
# See also LICENSE.txt
""" zope-org-valuation [OPTIONS] [project_name]*

Print SLOC and COCOMO valuation of projects on standard output as a CSV file.

Options:

--help, -h, -?      Print this usage message and exit.

--quiet, -q         Suppress inessential output (on standard error).

--verbose, -v       Add more noisy output (on standard error).

--source-dir, -s    Use the supplied value as the directory into which
                    checkouts are made for each project.  Defaults to
                    'work/src'.  This directory must exist.

--data-dir, -d      Use the supplied value as the directory into which
                    'sloccount' stores its computed information.
                    Defaults to 'work/data'.  If this directory exists, it
                    should not have any valuable content:  it will be removed
                    and recreated during the run.
"""
import os
import sys
import getopt

from subvertpy.client import Client
from subvertpy.ra import RemoteAccess

from zope.assetvaluation.valuation import Assessor


class Checker(object):

    root = 'svn://svn.zope.org/repos/main'

    def __init__(self, src_dir, data_dir, projects, verbosity):
        self.repos = RemoteAccess(self.root)
        self.src_dir = src_dir
        self.data_dir = data_dir
        self.projects = projects
        self.verbosity = verbosity

    def run(self):
        branches = {}
        for project, branch in self.list_projects_branches():
            branches[project] = branch
            c = Client()
            p_dir = os.path.join(self.src_dir, project)
            c.checkout(url='%s/%s/%s' % (self.root, project, branch),
                       path=p_dir, rev='HEAD', ignore_externals=True)
            assessor = Assessor(p_dir, self.data_dir)
            sloc, cost = assessor()
            yield project, branch, sloc, cost

    def log(self, message, level=1):
        if level <= self.verbosity:
            print >> sys.stderr, message

    def list_projects_branches(self):
        projects = self.projects or self.repos.get_dir('/')[0].keys()
        for project in projects:
            if project == 'README.txt':
                continue
            self.log('Project: %s' % project)
            top = self.repos.get_dir(project)[0].keys()
            if 'trunk' in top:
                self.log('  branch: trunk', 2)
                yield project, 'trunk'
            elif 'develop' in top:
                self.log('  branch: develop', 2)
                yield project, 'develop'


CSV_HEADER = '"Project","Branch","SLOC","Cost"'
CSV_ROW = '"%s","%s",%d,%d'

def usage(error='', rc=1):
    print >>sys.stderr, __doc__
    if error:
        print >>sys.stderr
        print >>sys.stderr, error
    sys.exit(rc)

def main():
    src_dir = 'work/src'
    data_dir = 'work/data'
    verbosity = 1

    try:
        options, args = getopt.gnu_getopt(sys.argv[1:],
                                          'h?qvs:d:',
                                          ['help',
                                           'quiet',
                                           'verbose',
                                           'source-dir=',
                                           'data-dir=',
                                          ]
                                         )
    except getopt.GetoptError:
        usage(rc=1)

    for k, v in options:
        if k in ('-h', '-?', '--help'):
            usage(rc=2)
        if k in ('-q', '--quiet'):
            verbosity = 0
        if k in ('-v', '--verbose'):
            verbosity += 1
        if k in ('-s', '--source-dir'):
            src_dir = v
        if k in ('-d', '--data-dir'):
            data_dir = v

    src_dir = os.path.abspath(os.path.normpath(src_dir))
    if not os.path.isdir(src_dir):
        usage(error='No such source directory: %s' % src_dir)

    data_dir = os.path.abspath(os.path.normpath(data_dir))
    if not os.path.isdir(data_dir):
        os.makedirs(data_dir)

    print CSV_HEADER

    checker = Checker(src_dir, data_dir, args, verbosity)
    for project, branch, sloc, cost in checker.run():
        print CSV_ROW % (project, branch, sloc, cost)

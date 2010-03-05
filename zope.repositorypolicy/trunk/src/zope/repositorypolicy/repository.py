# Copyright (c) 2010 Zope Foundation and Contributors
# See also LICENSE.txt

import os
import re
import shutil
import subvertpy.client
import subvertpy.ra
import tempfile
import zope.repositorypolicy.project


RELEASE_BRANCH = re.compile(r'^[0-9]+\.[0-9]+$')


class Checker(object):

    root = 'svn://svn.zope.org/repos/main'

    def __init__(self):
        self.repos = subvertpy.ra.RemoteAccess(self.root)

    def run(self):
        for project, branch in self.list_projects_branches():
            working_dir = tempfile.mkdtemp()
            os.chdir(working_dir)
            try:
                c = subvertpy.client.Client()
                c.checkout(url='%s/%s/%s' % (self.root, project, branch),
                           path=working_dir, rev='HEAD')
                checker = zope.repositorypolicy.project.Checker(working_dir)
                checker.run()
                for entry in checker.log:
                    yield '%s/%s:%s' % (project, branch, entry)
            finally:
                shutil.rmtree(working_dir)

    def list_projects_branches(self):
        for project in self.repos.get_dir('/')[0].keys():
            top = self.repos.get_dir(project)[0].keys()
            if 'trunk' in top:
                yield project, 'trunk'
            if 'branches' in top:
                branches = self.repos.get_dir(
                    '%s/branches' % project)[0].keys()
                releases = []
                for branch in branches:
                    if not RELEASE_BRANCH.match(branch):
                        continue
                    releases.append([int(x) for x in branch.split('.')])
                releases.sort()
                for release in releases[-2:]:
                    release = '.'.join(str(x) for x in release)
                    yield project, 'branches/%s' % release


def main():
    result = 0
    checker = Checker()
    for entry in checker.run():
        result = 1
        print entry
    sys.exit(result)

# Copyright (c) 2010 Zope Foundation and Contributors
# See also LICENSE.txt

import datetime
import os
import re
import shutil
import smtplib
import subvertpy.client
import subvertpy.ra
import sys
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
                           path=working_dir, rev='HEAD', ignore_externals=True)
                checker = zope.repositorypolicy.project.Checker(working_dir)
                checker.run()
                for entry in checker.log:
                    yield (project, branch, entry)
            finally:
                shutil.rmtree(working_dir)

    def list_projects_branches(self):
        for project in self.repos.get_dir('/')[0].keys():
            if project == 'README.txt':
                continue
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

MAIL_TEMPLATE = """\
The packages and branches listed below have failed one or
more repository policy checks. To see more detailed output,
use the "zope.repositorypolicy" package and run its script
"zope-org-check-project" against a checkout of the branch
in question.

The full log of errors can be found here: %(log_url)s

Summary
-------

%(project_branches)s
--\x20
This message was generated automatically.
"""


def main_mail():
    smtp_host, sender_address, target_address, httpbase, logbase = sys.argv[1:]

    stamp = datetime.datetime.now().isoformat()
    logname = 'report-%s.txt' % stamp
    log = open(os.path.join(logbase, logname), 'w')

    projects = {}

    checker = Checker()
    for project, branch, error in checker.run():
        projects.setdefault(project, set())
        projects[project].add(branch)
        log.write('%s/%s:%s\n' % (project, branch, error))
    log.close()

    if projects:
        subject = ('FAILURE: Repository policy check found '
                   'errors in %s projects' % len(projects))
    else:
        subject = 'OK: Repository policy check found no errors'

    mail = {}
    mail['log_url'] = httpbase + '/' + logname
    mail['project_branches'] = ''
    for project in sorted(projects):
        mail['project_branches'] += (
            project + '\n' +
            ''.join('\t%s\n' % x for x in projects[project]))

    body = MAIL_TEMPLATE % mail

    mailserver = smtplib.SMTP(smtp_host)
    msg = ('From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s' %
            (sender_address, target_address, subject, body))
    mailserver.sendmail(sender_address, [target_address], msg)
    mailserver.quit()

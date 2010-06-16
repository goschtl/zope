# encoding: utf-8
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
# Created by Charlie Clark on 2010-04-06.
#
# Uses lauchpadlib, https://edge.launchpad.net/+apidoc/1.0.htmls
# Particularly the projects 'collection' and project and bug_task 'entries'
#
# N.B. bug_tasks are not the same as bugs.
##############################################################################
# $Id$
""" checkbugs

Check which Launchpad bugs for a project or project have been marked as
in a given status (default 'New') for at least a number of days (default 14).

Usage:

 $ checkbugs [OPTIONS] [project-name]*

Options
-------

--help, -h, -?       Display this usage message and exit.

--version, -V        Print the version of the script and exit.

--quiet, -q          Emit less output.

--verbose, -v        Emit more output.

--num-days, -n       Set the number of days old a bug must be to be reported
                     (defaults to 14).

--state, -s          Set the state used to find bugs (defaults to "New";
                     allowed values include:

                     New
                     "Incomplete (with response)",
                     "Incomplete (without response)"
                     Incomplete
                     Invalid
                     "Won't Fix"
                     Confirmed
                     Triaged
                     "In Progress"
                     "Fix Committed"
                     "Fix Released"
                     
                     May be repeated.

                     Note that you need to quote any values containing spaces.

--project-group, -g  Supply a named project group.  If no project names are
                     passed, use the project group to look up a list of project
                     names

--mail, -m           Send report as e-mail. Must also supply at least a "to"
                     and "from" address. Host will default to localhost if
                     none is supplied here.

--mail-from          Address sending an e-mail report

--mail-to            Address e-mail report will be sent to

"""

import datetime
import getopt
import sys
import smtplib
import StringIO

from launchpadlib.launchpad import Launchpad
from pytz import utc

class BugTracker(object):
    """Check the BugTracker for new bugs"""
    
    def __init__(self, launchpad, project, report_date, states, rheostat):
        """Log into launchpad and get the Zope 3 project
        """
        self.project_name = project
        self.report_date = report_date
        self.states = states
        self.rheostat = rheostat
        self.project = launchpad.projects[project]
        self.bugs = []
    
    def get(self):
        """Get all new bugs and list those reported more than
        two weeks ago.
        Have to fumble with the reported creation date as it has a timezone
        """
        bugs = self.project.searchTasks(status=tuple(self.states))
        for (idx, bug) in enumerate(bugs):
            date_created = datetime.date(*bug.date_created.timetuple()[:3])
            if date_created < self.report_date:
                # lame, I know, but the bug's own link is on the 'edge'
                # domain.
                bug_id = bug.bug.id 
                link = ('https://bugs.launchpad.net/%s/+bug/%s'
                            % (self.project_name, bug_id))
                self.bugs.append({'title': bug.title,
                                  'link': link,
                                  'created': date_created.isoformat(),
                                  'status': bug.status,
                                  'assignee': bug.assignee,
                                  'id': bug_id,
                                 })
                
    def report(self):
        """Return a printable summary
        """
        count = len(self.bugs)
        self.rheostat(1, '-' * 78)
        self.rheostat(1, '%-40s: languishing bugs: %d'
                           % (self.project_name, count))
        self.rheostat(1, '-' * 78)

        for bug in self.bugs:
            if self.rheostat.verbose:
                fmt = ('%(title)s\n %(status)s %(created)s %(assignee)s\n'
                       ' %(link)s')
            else:
                fmt = '%(title)s\n %(link)s\n'
            self.rheostat(0, fmt % bug)
        return count

def get_projects_from_group(launchpad, project_group):
    group = launchpad.project_groups[project_group]
    return [x.name for x in group.projects]

class Rheostat:

    def __init__(self, verbose):
        self.verbose = verbose

    def __call__(self, level, message):
        if level <= self.verbose:
            print message

def mail_it(mail_host, mail_from, mail_to, subject, report):
    """Send report as e-mail"""

    mail = {}
    mailserver = smtplib.SMTP(mail_host)
    msg = ('From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s' %
            (mail_from, mail_to, subject, report.getvalue()))
    mailserver.sendmail(mail_from, [mail_to], msg)
    mailserver.quit()

def main():
    verbose = 1
    days = 14
    states = []
    project_group = None
    sendmail = False
    mail_to = None
    mail_from = None
    try:
        options, args = getopt.gnu_getopt(sys.argv[1:],
                                          '?hqvn:s:g:m',
                                          ['help',
                                           'verbose',
                                           'quiet',
                                           'num-days=',
                                           'state=',
                                           'project-group=',
                                           'mail=',
                                           'mail-from=',
                                           'mail-to='
                                          ])
    except getopt.GetoptError, e:
        print __doc__
        print
        print str(e)
        sys.exit(1)

    for k, v in options:
        if k in ('-h', '-?', '--help'):
            print __doc__
            sys.exit(2)
        elif k in ('-q', '--quiet'):
            verbose = 0
        elif k in ('-v', '--verbose'):
            verbose += 1
        elif k in ('-n', '--num-days'):
            days = int(v)
        elif k in ('-s', '--state'):
            states.append(v)
        elif k in ('-g', '--project-group'):
            project_group = v
        elif k in ('-m', '--mail'):
            sendmail = True
            mail_host = v or 'localhost'
        elif k == '--mail-to':
            mail_to = v
        elif k == '--mail-from':
            mail_from = v
        else:
            print __doc__
            sys.exit(1)
    if sendmail is True:
        if not (mail_to or mail_from):
            print "Mail addresses must be supplied"
            sys.exit(1)
        else:
            report = StringIO.StringIO()
            sys.stdout = report

    today = datetime.date.today()
    delta = datetime.timedelta(days=days)
    report_date = today - delta

    if not states:
        states.append('New')

    rheostat = Rheostat(verbose)

    start = datetime.datetime.now(utc)
    rheostat(1, '=' * 78)
    rheostat(1, 'Languishing bugs report:   %s'
                    % start.strftime('%Y-%m-%dT%H:%M%Z'))
    rheostat(1, '=' * 78)
    rheostat(1, 'States included:  %s' % (', '.join(states)))
    rheostat(1, 'Minimum age:      %s' % days)
    rheostat(1, '')

    launchpad = Launchpad.login_anonymously("Zope Bugtracker", "edge")

    if args:
        projects = args
    elif project_group is not None:
        projects = get_projects_from_group(launchpad, project_group)
    else:
        projects = ['zope3']

    total = 0
    for project in projects:
        Tracker = BugTracker(launchpad, project, report_date, states, rheostat)
        Tracker.get()
        total += Tracker.report()

    rheostat(1, '=' * 78)
    rheostat(0, 'Total languishing bugs:  %d' % total)
    rheostat(1, '=' * 78)

    if total == 0:
        status = 'OK'
    else:
        status = 'FAILURE'

    if sendmail is True:
        mail_it(mail_host, mail_from, mail_to, 
                '%s: Total languishing bugs:  %d' % (status, total), report)
    if total > 0:
        sys.exit(-1)

if __name__ == '__main__':
    main()

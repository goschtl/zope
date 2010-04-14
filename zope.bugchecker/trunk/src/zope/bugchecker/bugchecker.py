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
"""

import datetime
import getopt
import sys

from launchpadlib.launchpad import Launchpad

class BugTracker(object):
    """Check the BugTracker for new bugs"""
    
    def __init__(self, launchpad, project, report_date, states, verbose):
        """Log into launchpad and get the Zope 3 project
        """
        self.project_name = project
        self.report_date = report_date
        self.states = states
        self.verbose = verbose
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
                self.bugs.append({'title': bug.title,
                                  'link': bug.bug_link,
                                  'created': date_created.isoformat(),
                                  'status': bug.status,
                                 })
                
    def report(self):
        """Return a printable summary
        """
        count = len(self.bugs)
        lines = ['-' * 78 +
                 '\n%-40s: languishing bugs: %d\n'
                    % (self.project_name, count) +
                 '-' * 78
                ]
        for bug in self.bugs:
            if self.verbose:
                fmt = '%(title)s\n %(status)s %(created)s\n %(link)s'
            else:
                fmt = '%(title)s\n %(link)s'
            lines.append(fmt % bug)
        return count, "\n\n".join(lines)

def get_projects_from_group(launchpad, project_group):
    group = launchpad.project_groups[project_group]
    return [x.name for x in group.projects]

def main():
    verbose = 1
    days = 14
    states = []
    project_group = None
    try:
        options, args = getopt.gnu_getopt(sys.argv[1:],
                                          '?hqvn:s:g:',
                                          ['help',
                                           'verbose',
                                           'quiet',
                                           'num-days=',
                                           'state=',
                                           'project-group=',
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
        else:
            print __doc__
            sys.exit(1)

    today = datetime.date.today()
    delta = datetime.timedelta(days=days)
    report_date = today - delta
    launchpad = Launchpad.login_anonymously("Zope Bugtracker", "edge")

    if args:
        projects = args
    elif project_group is not None:
        projects = get_projects_from_group(launchpad, project_group)
    else:
        projects = ['zope3']

    if not states:
        states.append('New')

    total = 0
    for project in projects:
        Tracker = BugTracker(launchpad, project, report_date, states, verbose)
        Tracker.get()
        count, text = Tracker.report()
        total += count
        print text

    print '=' * 78
    print 'Total:  %d' % total
    print '=' * 78

    if total > 0:
        sys.exit(-1)

if __name__ == '__main__':
    main()

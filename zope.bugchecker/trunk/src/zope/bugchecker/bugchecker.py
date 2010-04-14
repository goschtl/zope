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
##############################################################################
"""
bugtracker.py

$Id$

Check which bugs have been marked as 'new' for at least
14 days

Uses lauchpadlib
https://edge.launchpad.net/+apidoc/1.0.htmls
Particularly the projects 'collection' and project and bug_task 'entries'
N.B. bug_tasks are not the same as bugs.

Created by Charlie Clark on 2010-04-06.
"""

import datetime
from launchpadlib.launchpad import Launchpad

today = datetime.date.today()
two_weeks = datetime.timedelta(days=14)
report_date = today - two_weeks

class BugTracker(object):
    """Check the BugTracker for new bugs"""
    
    def __init__(self, project):
        """Log into launchpad and get the Zope 3 project
        """
        self.project = project
        launchpad = Launchpad.login_anonymously("Zope Bugtracker", "edge")
        self.project = launchpad.projects[project]
        self.bugs = []
    
    def get(self):
        """Get all new bugs and list those reported more than
        two weeks ago.
        Have to fumble with the reported creation date as it has a timezone
        """
        bugs = self.project.searchTasks(status=('New',))
        for (idx, bug) in enumerate(bugs):
            date_created = datetime.date(*bug.date_created.timetuple()[:3])
            if date_created < report_date:
                self.bugs.append("%s\n%s" % (bug.title, bug.bug_link))
                
    def report(self):
        """Return a printable summary
        """
        lines = ['Languishing bugs for: %s' % self.project]
        lines.extend(self.bugs)
        return "\n\n".join(lines)

def main(*projects):
    if not projects:
        import sys
        projects = sys.argv[1:] or ['zope3']
    for project in projects:
        Tracker = BugTracker(project)
        Tracker.get()
        print Tracker.report()

if __name__ == '__main__':
    main(sys.argv[1:])

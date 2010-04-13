#!/Users/charlieclark/temp/zope/bin/python
# encoding: utf-8
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
Copyright (c) 2010 Zope Foundation and Contributors
"""

import datetime
from launchpadlib.launchpad import Launchpad

today = datetime.date.today()
two_weeks = datetime.timedelta(days=14)
report_date = today - two_weeks

class BugTracker(object):
    """Check the BugTracker for new bugs"""
    
    def __init__(self):
        """Log into launchpad and get the Zope 3 project"""
        launchpad = Launchpad.login_anonymously("Zope Bugtracker", "edge")
        self.project = launchpad.projects['zope3']
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
        """Return a printable summary"""
        return "\n\n".join(self.bugs)

if __name__ == '__main__':
    Tracker = BugTracker()
    Tracker.get()
    print Tracker.report()

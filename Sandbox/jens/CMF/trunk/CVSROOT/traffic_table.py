"""Table dictating what goes where for the traffic_cop module.

The global var 'table' contains a list of entries identifying where
change-notifications for particular sections of the repository are sent.

Each 'table' entry is a dictionary containing some mandatory and some
optional fields (optional fields have default values described)

 - 'addrs' - a list of email addresses for checkin notice delivery. 

 - 'path' - to the repository dir, relative to the CVSROOT.  If the
   leading path of the files being checked in (re) match the value of this
   attribute, then this entry is invoked.

   NOTE that the comparison mechanism takes into account the repository
   symlinks (as dictated by the repolinks file).  This means that all
   entries for directories that contain the checked-in files by virtue of
   symlinks, as well as by direct containment, will qualify - the system
   takes care of unravelling the symlinks for you.

\(Most of the original ssh/rsync-based mirroring was stripped out of this
file after version 1.87.)"""

zopeaddr = ["zope-checkins@zope.org"]

_TABLE = []

def add_to_table(entries, prepend=0):
    global _TABLE
    if type(entries) not in [type([]), type(())]:
        entries = [entries]
    if prepend:
        _TABLE = entries + _TABLE
    else:
        _TABLE = _TABLE + entries

def add_multipath(paths, addrs):
    """Add entries with different paths but the same addrs and remote"""
    for path in paths:
        add_to_table({'path': path,
                      'addrs': addrs})

def get_table():
    return _TABLE[:]

def init_table():
    add_to_table([
        {'path': "CVSROOT",
         'addrs': ["zope-cvs@zope.org"],
         'specials': [("repolinks", "adjustlinks.py")],
         'verbose': 1},

##       {'path': "test",
##        'addrs': "klm@zope.com"},

        # Catchall for when *no other entry* matches:
        {'path': None,
         'verbose': 1,
         'addrs': ["zope-cvs@zope.org"]},

        {'path': "Operations",
         'addrs': ["support@zope.com"]},

        {'path': "Zope",
         'addrs': zopeaddr},

        {'path': "StandaloneZODB",
         'addrs': ["zodb-checkins@zope.org"]},
        
        {'path': "CMF",
         'addrs': ['cmf-checkins@zope.org']},

        {'path': "Products/CMFDemo",
         'addrs': ["cmf-checkins@zope.org"]},

        {'path': "Packages/TAL",
         'addrs': ["zpt@mail.zope.org"]},
        {'path': "Products/PageTemplates",
         'addrs': ["zpt@mail.zope.org"]},
        {'path': "Packages/ZTUtils",
         'addrs': ["zpt@mail.zope.org"]},
        {'path': "Products/PresentationTemplates",
         'addrs': ["zpt@mail.zope.org"]},

        {'path': "Packages/Spread",
         'addrs': ["pythonlabs@zope.com"]},

        {'path': "Products/ParsedXML",
         'addrs': ["parsed-xml-dev@mail.zope.org"]},

        {'path': "ZEO",
         'addrs': ['zeo-checkins@zope.org',
                   'zodb-checkins@zope.org']},

        {'path': "ZopeDocs",
         'addrs': 'zopedocs-checkins@zope.org'},

        {'path': "Docs",
         'addrs': 'zope-book@zope.org'},

        {'path': "ZopeMozilla",
         'addrs': 'zope-mozilla@zope.org'},

        {'path': "Products/TrackerBase",
         'addrs': ['tracker-dev@zope.org']},

        {'path': "Projects/python-site",
         'addrs': ["pythonlabs@zope.com"]},

        {'path': "Products/DCOracle2",
         'addrs': ["zope-checkins@zope.org"]},
    ])

init_table()

"""Table dictating what goes where for the traffic_cop module.

the global var 'table' contains a list of entries identifying project dirs
to be mirrored.

Custom (local, consulting-business) entries should go in
/cvs-repository/custom_traffic_table.py, which is not mirrored in the
public repository.

Each 'table' entry is a dictionary containing some mandatory and some
optional fields (optional fields have default values described)

 - 'path' - to the repository dir, relative to the CVSROOT.  This is used
   both as path for identifying qualifying checkins and also as a path to
   specify the directory within which rsync will be applied.

 - 'excludes' - a regular expression identifying items within the
   qualifying repository directory that should be excluded.  (Be careful
   with your regular expressions - the 're' module will be used only if the
   local python installation has re, or else the old 'regex' module will be
   used.  So you may want to use simple regular expressions that work for
   both.)  It is passed to rsync, so see the section of the rsync man page
   about exclude patterns for details.  Default is for nothing to be
   excluded.

 - 'addrs' - a list of addresses to which checkin messages should be delivered.

 - 'remote' - specifying the repository to which checkins should be synced.
   This dictionary must have the following fields:

    'host' - string naming the remote host
    'acct' - the pserver acct that should have access (XXX not yet implemented)
    'repodir' - the repository directory to which syncs should be done.
    'leading_path' - if any, substitute as leading path for remote component.
    'receiver_id' - account id of receiving account.

   The default value used for every entry is dictated by a module global
   variable, 'remote'.

   If 'remote' is set to None, then no remote setting is used.  (This is
   useful for cases where no mirroring is to be done, particularly useful when 
   the checkins are happening at the mirror site, eg when public checkins are 
   happening.)
"""

# Default is *no* remote - people explicitly propagation if they want it.
remote = None
public_remote = {'host': "cvs.zope.org",
                 'acct': "anonymous",
                 'repodir': "/cvs-repository"}
products_remote = {'host': "cvs.zope.org",
                   'acct': "anonymous",
                   'repodir': "/cvs-repository",
                   'leading_path': "/Products/DC"}

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

def get_table():
    return _TABLE[:]

def init_table():
    add_to_table([
        {'path': "CVSROOT",
         'remote': public_remote,
         'addrs': ["digicool-cvs@zope.org"],
         'excludes': ["/history"]},

##        {'path': "test",
##         'remote': public_remote,
##         'host': "cvs.zope.org",
##         'addrs': "klm@digicool.com"},

        {'path': "Operations",
         'addrs': "support@digicool.com",
         'remote': None},

        {'path': "Zope2",
         'remote': public_remote,
         'addrs': zopeaddr},

        {'path': "Packages/ZEO",
         'remote': public_remote,
         'addrs': ['zeo-checkins@zope.org']},

        {'path': "ZopeDocs",
         'addrs': 'zopedocs-checkins@zope.org',
         'remote': None},

#        {'path': "Documentation/Guides/Book",
#         'addrs': 'zope-book@zope.org',
#         'remote': None},

        {'path': "ZopeMozilla",
         'addrs': 'zope-mozilla@zope.org',
         'remote': None},

        {'path': "ZopePTK",
         'addrs': 'zope-ptk@zope.org',
         'remote': None},

        {'path': "Packages/Products/XMLDocument",
         'addrs': zopeaddr,
         'remote': products_remote},

        {'path': "Packages/Products/PythonMethod",
         'addrs': None,
         'remote': products_remote},

        {'path': "Packages/Products/TrackerBase",
         'addrs': ['tracker-dev@zope.org'],
         'remote': products_remote},

        {'path': "Packages/Products/ImageCache",
         'addrs': None,
         'remote': products_remote},

        {'path': "Packages/Products/ParsedXML",
         'addrs': ["parsed-xml-dev@mail.zope.org"],
         'remote': products_remote},
    ])

init_table()

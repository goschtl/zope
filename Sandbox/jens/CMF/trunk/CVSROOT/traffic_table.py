"""Table dictating what goes where for the traffic_cop module.

The global var 'table' contains a list of entries identifying where
change-notifications for particular sections of the repository are sent.  (You
can also use the entries to identify mirroring target hosts, but that's not
longer used.)

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

 The 'remote' entry is no longer particularly useful - in fact, we haven't yet
 instituted rsync on the host system - so the following can be ignored:

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

# Default is *no* remote - explicitly specify propagation if you want it.
remote = None
public_remote = None
products_remote = None

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

def add_multipath(paths, addrs, remote):
    """Add entries with different paths but the same addrs and remote"""
    for path in paths:
        add_to_table({'path': path,
                      'addrs': addrs,
                      'remote': remote})

def get_table():
    return _TABLE[:]

def init_table():
    add_to_table([
        {'path': "CVSROOT",
         'addrs': ["digicool-cvs@zope.org"],
         'excludes': ["/history"]},

##       {'path': "test",
##        'remote': None,
##        'addrs': "klm@digicool.com"},

        # Catchall for when *no other entry* matches:
        {'path': None,
         'addrs': ["digicool-cvs@zope.org"]},

        {'path': "Operations",
         'addrs': ["support@digicool.com"]},

        {'path': "Releases/Zope", 'addrs': zopeaddr},
        {'path': "Packages", 'addrs': zopeaddr},
        {'path': "Products/__init__.py", 'addrs': zopeaddr},
        {'path': "Products/ExternalMethod", 'addrs': zopeaddr},
        {'path': "Products/ImageCache", 'addrs': None},
        {'path': "Products/MIMETools", 'addrs': zopeaddr},
        {'path': "Packages/MailHost", 'addrs': zopeaddr},
        {'path': "Products/OFSP", 'addrs': zopeaddr},
        {'path': "Products/PluginIndexes", 'addrs': zopeaddr},
        {'path': "Products/XMLDocument", 'addrs': zopeaddr},
        {'path': "Products/PythonMethod", 'addrs': None},
        {'path': "Products/STXDocument", 'addrs': zopeaddr},
        {'path': "Products/SiteAccess", 'addrs': zopeaddr},
        {'path': "Products/StandardCacheManagers", 'addrs': zopeaddr},
        {'path': "Products/ZCatalog", 'addrs': zopeaddr},
        {'path': "Products/ZGadflyDA", 'addrs': zopeaddr},
        {'path': "Products/ZSQLMethods", 'addrs': zopeaddr},
        {'path': "Products/ZopeTutorial", 'addrs': zopeaddr},

        {'path': "Packages/TAL", 'addrs': ["zpt@mail.zope.org"]},

        {'path': "Products/PageTemplates", 'addrs': ["zpt@mail.zope.org"]},
        {'path': "Products/PresentationTemplates",
         'addrs': ["zpt@mail.zope.org"]},

        {'path': "Products/ParsedXML",
         'addrs': ["parsed-xml-dev@mail.zope.org"]},

        {'path': "Packages/ZEO",
         'addrs': ['zeo-checkins@zope.org']},

        {'path': "ZopeDocs",
         'addrs': 'zopedocs-checkins@zope.org'},

#        {'path': "Documentation/Guides/Book",
#         'addrs': 'zope-book@zope.org'},

        {'path': "ZopeMozilla",
         'addrs': 'zope-mozilla@zope.org'},

        {'path': "CMF",
         'addrs': 'cmf-checkins@zope.org'},
        {'path': "Products/CMF", 'addrs': 'cmf-checkins@zope.org'},
        {'path': "Products/DCWorkflow", 'addrs': 'cmf-checkins@zope.org'},

        {'path': "Products/TrackerBase",
         'addrs': ['tracker-dev@zope.org']},

        {'path': "Projects/python-site",
         'addrs': ["pythonlabs@digicool.com"]},

        {'path': "Products/CMFDemo",
         'addrs': ["karl@digicool.com", "adam@digicool.com"]},
        
    ])

# Support for the ZEO module (defined in CVSROOT/modules)

add_to_table({'path': "Releases/ZEO",
              'addrs': ("zodb-checkins@zope.org",)})

# Support for the StandaloneZODB module (defined in CVSROOT/modules)

add_to_table({'path': "Releases/StandaloneZODB",
              'addrs': ("zodb-checkins@zope.org",)})
              
add_multipath(("Zope2/lib/Components/ExtensionClass",
               "Packages/ZEO",
               "Zope2/lib/python/ZODB",
               "Zope2/lib/python/Persistence.py",
               "Zope2/lib/python/ThreadedAsync.py",
               "Zope2/lib/python/zLOG.py",
               "Zope2/lib/python/zdaemon.py",
               "Packages/StorageGC",
               "Packages/bsddb3Storage",
               ),
              ("zodb-checkins@zope.org",),
              None)

add_to_table({'path': "Packages/bsddb3Storage",
              'addrs': ("zodb-checkins@zope.org",)})

init_table()

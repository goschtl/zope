"""Table dictating what goes where for the traffic_cop module.

the global var 'table' contains a list of entries identifying project dirs
to be mirrored.

Each 'table' entry is a dictionary containing some mandatory and some
optional fields (optional fields have default values described)

 - 'path' - to the repository dir, relative to the CVSROOT.  This is used
   both as path for identifying qualifying checkins and also as a path to
   specify the directory within which rsync will be applied.

 - 'excludes' - a regular expression identifying items within the
   qualifying repository directory that should be excluded.  It is passed
   to rsync, so see the section of the rsync man page about exclude
   patterns for details.  Default is for nothing to be excluded.

 - 'addrs' - a list of addresses to which checkin messages should be delivered.

 - 'remote' - specifying the repository to which checkins should be synced.
   This dictionary must have the following fields:

    'host' - string naming the remote host
    'acct' - the pserver acct that should have access (not yet implemented)
    'repodir' - the repository directory to which syncs should be done.

   The default value used for every entry is dictated by a module global
   variable, 'remote'.

"""

remote = {'host': "www.zope.org",
          'acct': "anonymous",
          'repodir': "/cvs-repository"}

tmpaddr = ["klm@digicool.com"]
zopeaddr = ["klm@digicool.com"]

table = [
    {'path': "CVSROOT", 'addrs': ["digicool-cvs@zope.org"],
     'excludes': ["/history"]},

    {'path': "test", 'addrs': tmpaddr},

    {'path': "Components/GreyThing", 'addrs': tmpaddr},
    {'path': "Components/ZopeHTTPServer", 'addrs': tmpaddr},
    {'path': "Components/ExtensionClass", 'addrs': tmpaddr},
    {'path': "Components/BTree", 'addrs': tmpaddr},
    {'path': "Components/cPickle", 'addrs': tmpaddr},
    {'path': "Components/zlib", 'addrs': tmpaddr},
    {'path': "Components/pcgi2", 'addrs': tmpaddr},
    {'path': "Packages/AccessControl", 'addrs': tmpaddr},
    {'path': "Packages/App", 'addrs': tmpaddr},
    {'path': "Packages/BoboPOS", 'addrs': tmpaddr},
    {'path': "Packages/DateTime", 'addrs': tmpaddr},
    {'path': "Packages/DocumentTemplate", 'addrs': tmpaddr},
    {'path': "Packages/HelpSys", 'addrs': tmpaddr},
    {'path': "Packages/ZPublisher", 'addrs': tmpaddr},
    {'path': "Packages/OFS", 'addrs': tmpaddr},
    {'path': "Packages/Scheduler", 'addrs': tmpaddr},
    {'path': "Packages/StructuredText", 'addrs': tmpaddr},
    {'path': "Packages/TreeDisplay", 'addrs': tmpaddr},
    {'path': "Packages/SearchIndex", 'addrs': tmpaddr},
    {'path': "Packages/ZClasses", 'addrs': tmpaddr},
    {'path': "Packages/Shared", 'addrs': tmpaddr},
    {'path': "Packages/webdav", 'addrs': tmpaddr},
    {'path': "Packages/Products/__init__.py", 'addrs': tmpaddr},
    {'path': "Packages/Products/OFSP", 'addrs': tmpaddr},
    {'path': "Packages/Products/MailHost", 'addrs': tmpaddr},
    {'path': "Packages/Products/ExternalMethod", 'addrs': tmpaddr},
    {'path': "Packages/Products/ZSQLMethods", 'addrs': tmpaddr},
    {'path': "Packages/Products/ZGadflyDA", 'addrs': tmpaddr},
    {'path': "Packages/Products/etcUserFolder", 'addrs': tmpaddr},
]

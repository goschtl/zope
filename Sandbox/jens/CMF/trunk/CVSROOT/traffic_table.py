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

zopeaddr = ["klm@digicool.com"]

table = [
    {'path': "test", 'addrs': zopeaddr},
    {'path': "CVSROOT", 'addrs': zopeaddr, 'excludes': ["/history"]},
    {'path': "Components/GreyThing", 'addrs': zopeaddr},
    {'path': "Components/ZopeHTTPServer", 'addrs': zopeaddr},
    {'path': "Components/ExtensionClass", 'addrs': zopeaddr},
    {'path': "Components/BTree", 'addrs': zopeaddr},
    {'path': "Components/cPickle", 'addrs': zopeaddr},
    {'path': "Components/zlib", 'addrs': zopeaddr},
    {'path': "Components/pcgi2", 'addrs': zopeaddr},
    {'path': "Packages/AccessControl", 'addrs': zopeaddr},
    {'path': "Packages/App", 'addrs': zopeaddr},
    {'path': "Packages/BoboPOS", 'addrs': zopeaddr},
    {'path': "Packages/DateTime", 'addrs': zopeaddr},
    {'path': "Packages/DocumentTemplate", 'addrs': zopeaddr},
    {'path': "Packages/HelpSys", 'addrs': zopeaddr},
    {'path': "Packages/ZPublisher", 'addrs': zopeaddr},
    {'path': "Packages/OFS", 'addrs': zopeaddr},
    {'path': "Packages/Scheduler", 'addrs': zopeaddr},
    {'path': "Packages/StructuredText", 'addrs': zopeaddr},
    {'path': "Packages/TreeDisplay", 'addrs': zopeaddr},
    {'path': "Packages/SearchIndex", 'addrs': zopeaddr},
    {'path': "Packages/ZClasses", 'addrs': zopeaddr},
    {'path': "Packages/Shared", 'addrs': zopeaddr},
    {'path': "Packages/webdav", 'addrs': zopeaddr},
    {'path': "Packages/Products/__init__.py", 'addrs': zopeaddr},
    {'path': "Packages/Products/OFSP", 'addrs': zopeaddr},
    {'path': "Packages/Products/MailHost", 'addrs': zopeaddr},
    {'path': "Packages/Products/ExternalMethod", 'addrs': zopeaddr},
    {'path': "Packages/Products/ZSQLMethods", 'addrs': zopeaddr},
    {'path': "Packages/Products/ZGadflyDA", 'addrs': zopeaddr},
    {'path': "Packages/Products/etcUserFolder", 'addrs': zopeaddr},
]

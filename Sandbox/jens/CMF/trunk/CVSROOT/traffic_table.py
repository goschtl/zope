"""Table dictating what goes where for the traffic_cop module.

A list of entries for each project that has anything going anywhere.

Each entry is a tuple containing:

 - a string name for the entry - often the repository dir

 - a regular expression qualifying checkins for membership
   - matched against the repository path of the checkin, sans CVSROOT

 - a list of addresses for delivery of checkin message

 - an optional dictionary specifying the remote host to which repository
   checkins should be synced.  The fields are:

    'host'
    'acct' - the pserver acct that will get access
    'repodir' - the repository directory to which syncs should be done

   It's generally convenient to have a module variable, eg "MIRROR",
   for the default host used in most entries.

E.g.: 

MIRROR = {'host': "www.zope.org",
          'acct': "anonymous",
          'repodir': "/cvs-repository"}
("test", "^test", ["klm@digicool.com"], MIRROR)
"""

MIRROR = {'host': "www.zope.org",
          'acct': "anonymous",
          'repodir': "/cvs-repository"}

table = [
    ("test", "^test", ["klm@digicool.com"], MIRROR),
    ("CVSROOT", "^CVSROOT", ["klm@digicool.com"], MIRROR)
]

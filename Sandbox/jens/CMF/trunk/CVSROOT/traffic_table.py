"""Table dictating what goes where for the traffic_cop module.

the global var 'table' contains a list of entries identifying project dirs
to be mirrored.

Each 'table' entry is a tuple containing:

 - a string name for the entry - often the repository dir

 - inclusions - a regular expression identifying the checkins that qualify
   for treatment; it's matched against the repository path of the checkin,
   sans CVSROOT

 - exclusions - a regular expression identifying checkins that *would*
   qualify according to the previous expresion, but should be excluded.
   A value of None means no exclusions.

 - a list of addresses to which checkin messages should be delivered

 - an dictionary specifying the remote host to which repository
   checkins should be synced.  The fields are:

    'host'
    'acct' - the pserver acct that will get access
    'repodir' - the repository directory to which syncs should be done. '%s'
                will be substituted with the entry's name, convenient for:

   It's generally convenient to have a module variable, eg "MIRROR",
   for the default host used in most entries.

E.g.: 


("test", "^test", None, ["klm@digicool.com"], {'host': "www.zope.org",
					       'acct': "anonymous",
					       'repodir': "%s"})
"""

MIRROR = {'host': "www.zope.org",
          'acct': "anonymous",
          'repodir': "/cvs-repository"}

table = [
    ("test", "^test", None, ["klm@digicool.com"], MIRROR),
    ("CVSROOT", "^CVSROOT", "^CVSROOT/history", ["klm@digicool.com"], MIRROR)
]

"""Table dictating what goes where for the traffic_cop module.

A list of entries for each project that has anything going anywhere.

Each entry is a tuple containing:

 - a string name for the entry

 - a regular expression qualifying checkins for membership
   - matched against the repository path of the checkin, sans CVSROOT

 - a list of addresses for delivery of checkin message

 - a dictionary specifying the remote host to which repository checkins
   should be synced.  The fields are:

    'host'
    'acct' - the pserver acct that will get access
    'repodir' - the repository directory to which syncs should be done

E.g.: 

 ("Test", "^test", ["klm@digicool.com"], {'host': "www.zope.org",
                                          'acct': "anonymous",
                                          'repodir': "/cvs-repository/test"])
"""

table = [
##  ("Test", "^test", ["klm@digicool.com"], {'host': "www.zope.org",
##                                           'acct': "anonymous",
##                                           'repodir': "/cvs-repository/test"])
 ("Test", "^test", [], {'host': "www.zope.org",
                                          'acct': "anonymous",
                                          'repodir': "/cvs-repository/test"])
]

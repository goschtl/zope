"""Table dictating what goes where for the traffic_cop module.

A list of entries for each project that has anything going anywhere.

Each entry is a list of strings, containing:

 - a name for the entry
 - a regular expression qualifying checkins for membership
   - matched against the repository path of the checkin, sans CVSROOT
 - list of addresses for delivery of checkin message
 - list of strings naming pserver accounts to be given checkout access
   (currently only "anonymous" is supported).

E.g.:

 ["Test", "^test", ["klm@digicool.com"], ["anonymous"]]
"""

table = [
    ["Test", "^test", ["klm@digicool.com"], ["anonymous"]]
]

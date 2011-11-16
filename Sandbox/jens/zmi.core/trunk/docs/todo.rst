To do list
==========
This list does not claim to be a complete representation. It is a simple
memory aid and the place where the correlation between old Zope 2 ZMI
views and their templates is documented.

This is probably going to need some kind of adapter to provide the necessary
connection objects that are currently "magicked" into place.

Zope.App.ApplicationManager % Zope.App.CacheManager
---------------------------
| [ ] manage_workspace (?) # DatabaseChooser & www/chooseDatabase.pt, I think.
| [X] manage_main (dtml/dbMain) # Where the database is, size and opportunity to pack it
| [ ] manage_activity (dtml/activity) # Configurable chart of recent database activity
| [ ] manage_cacheParameters (dtml/manage_cacheParameters) # Database statistics
| [ ] manage_cacheGC (dtml/cacheGC) # Flush database
| [ ] manage_setHistoryLength (?)

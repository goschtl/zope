This directory contains utility scripts and modules that augment Zope.

To get detailed usage information, run any of these scripts without arguments:

  bbb.py -- Read and summarize a Zope database.
 
    This script illustrates how to read a database file outside of
    Zope and provides a number of options for finding bad data and 
    generating reports of data.

  load_site.py -- Load a Zope site from files and directories

    This script illustrates used of the Zope RPC mechanism, 
    ZPublisher.Client.  It provides some examples of pitfalls
    and their work-arounds.

  fixbbbts.py -- Fix database time stamps

    Sometimes, problems with system clocks can cause invalid time stamps
    to be written to databases.  The fixbbbts script can be used to 
    shift invalid times in the database to make them valid.


In addition to the scripts above, the following modules
are included:

  ppml.py  -- Python pickle markup language support

    This module supports conversion of Python pickles to 
    XML format.  Conversion from XML to Python pickle
    format is planned as well.




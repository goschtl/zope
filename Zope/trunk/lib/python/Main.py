############################################################################## 
#
#     Copyright 
#
#       Copyright 1996 Digital Creations, L.C., 910 Princess Anne
#       Street, Suite 300, Fredericksburg, Virginia 22401 U.S.A. All
#       rights reserved.
#
############################################################################## 
import ni, sys

import SimpleDB, Sync, TJar

class SyncDB(SimpleDB.Default, Sync.Synchronized):
    pass

SimpleDB.Default=SyncDB

import Globals

try:
    import thread
    Globals.application_lock=thread.allocate_lock()
    __bobo_before__=Globals.application_lock.acquire
    __bobo_after__ =Globals.application_lock.release
except: pass

import OFS.Application

import TreeDisplay.TreeTag
import Scheduler.Scheduler

# Open the application database
Bobobase=OFS.Application.open_bobobase()
SessionBase=Globals.SessionBase=TJar.TM(Bobobase)

bobo_application=app=Bobobase['Application']

##############################################################################
# Revision Log
#
# $Log: Main.py,v $
# Revision 1.11  1997/11/07 18:29:06  jim
# Added app alias.
#
# Revision 1.10  1997/11/07 17:32:30  jim
# Moved bobobase open to OFS.Application.
#
# Revision 1.9  1997/11/07 17:13:49  jim
# Added SessionBase.
#
# Revision 1.8  1997/10/31 17:04:18  brian
# *** empty log message ***
#
# Revision 1.7  1997/10/31 15:01:33  brian
# Fixed bug that could cause startup failure: when the bobobase failed to
# find 'Application' it would (on bsdi, anyway) raise AttributeError and
# only KeyError was being caught...
#
# Revision 1.6  1997/09/19 18:23:36  brian
# App nicification
#
# Revision 1.5  1997/09/17 16:17:00  jim
# Added scheduler hook.
#
# Revision 1.4  1997/09/10 15:55:50  jim
# Changed to use title_or_id.
#
# Revision 1.3  1997/09/02 21:22:06  jim
# Added import of TreeDisplay.TreeTag to enable tree tag.
# Changed document creation call.
#
# Revision 1.2  1997/08/28 19:32:36  jim
# Jim told Paul to do it
#
# Revision 1.1  1997/08/13 18:58:39  jim
# initial
#


"""Global definitions"""

__version__='$Revision: 1.9 $'[11:-2]


try:
    home=CUSTOMER_HOME,SOFTWARE_HOME,SOFTWARE_URL
    CUSTOMER_HOME,SOFTWARE_HOME,SOFTWARE_URL=home
except:
    # Debugger support
    import sys, os
    try: home=os.environ['SOFTWARE_HOME']
    except:
	home=os.getcwd()
        if home[-4:]=='/bin': home=home[:-4]
    CUSTOMER_HOME=sys.modules['__builtin__'].CUSTOMER_HOME=home
    SOFTWARE_HOME=sys.modules['__builtin__'].SOFTWARE_HOME=home
    SOFTWARE_URL=sys.modules['__builtin__'].SOFTWARE_URL=''



from SingleThreadedTransaction import PickleDictionary, Persistent
from SingleThreadedTransaction import PersistentMapping
import DocumentTemplate

class HTML(DocumentTemplate.HTML,Persistent,):
    "Persistent HTML Document Templates"

class HTMLDefault(DocumentTemplate.HTMLDefault,Persistent,):
    "Persistent Default HTML Document Templates"

class HTMLFile(DocumentTemplate.HTMLFile,Persistent,):
    "Persistent HTML Document Templates read from files"

    def __init__(self,name='',*args,**kw):
	args=(self, '%s/lib/python/%s.dtml' % (SOFTWARE_HOME,name),) + args
	apply(HTMLFile.inheritedAttribute('__init__'),args,kw)

data_dir     = CUSTOMER_HOME+'/var'
BobobaseName = '%s/Data.bbb' % data_dir

HTML.shared_globals['SOFTWARE_URL']=SOFTWARE_URL

from App.Dialogs import MessageDialog

SessionNameName='Principia-Session'


##########################################################################
#
# Log
#
# $Log: Globals.py,v $
# Revision 1.9  1997/11/21 19:33:45  brian
# Fixed out-of-date debugger support to add correct SH, CH, SU
#
# Revision 1.8  1997/11/07 17:12:15  jim
# Added SesionNameName.
#
# Revision 1.7  1997/09/15 17:03:53  jim
# Got rid of private.
#
# Revision 1.6  1997/09/02 21:39:43  jim
# Moved MessageDialog to end to deal with recursion in module imports.
#
# Revision 1.5  1997/08/28 19:32:36  jim
# Jim told Paul to do it
#
# Revision 1.4  1997/08/13 22:14:04  jim
# *** empty log message ***
#
# Revision 1.3  1997/08/13 21:42:45  jim
# Added back specialized HTMLFile
#
# Revision 1.2  1997/08/13 19:04:00  jim
# *** empty log message ***
#
# Revision 1.1  1997/08/13 18:58:39  jim
# initial
#
#



############################################################################## 
#
#     Copyright 
#
#       Copyright 1997 Digital Creations, L.C., 910 Princess Anne
#       Street, Suite 300, Fredericksburg, Virginia 22401 U.S.A. All
#       rights reserved.
#
############################################################################## 
__doc__='''MailHost Product Initialization
$Id: __init__.py,v 1.6 1998/01/05 19:34:12 jeffrey Exp $'''
__version__='$Revision: 1.6 $'[11:-2]

import MailHost, SendMailTag
from ImageFile import ImageFile

meta_types={'name':'Mail Host',
	    'action':'manage_addMailHost_form'
	    },

methods={
    'manage_addMailHost_form': MailHost.addForm,
    'manage_addMailHost':     MailHost.add,
    }

misc_={
    'MHIcon': ImageFile("www/MailHost_icon.gif", globals())
    }


"""External Method Product

This product provides support for external methods, which allow
domain-specific customization of web environments.
"""

from Acquisition import Explicit
from Globals import Persistent, HTMLFile, MessageDialog, HTML
import OFS.SimpleItem
from string import split, join, find, lower
import AccessControl.Role, sys, regex, traceback
from OFS.SimpleItem import pretty_tb
from App.Extensions import getObject, FuncCode

manage_addExternalMethodForm=HTMLFile('methodAdd', globals())

def manage_addExternalMethod(self, id, title, module, function, REQUEST=None):
    """Add an external method to a folder
  
    Un addition to the standard Principia object-creation arguments,
    'id' and title, the following arguments are defined:

	function -- The name of the python function. This can be a
	  an ordinary Python function, or a bound method.

	module -- The name of the file containing the function
	  definition.

	The module normally resides in the 'Extensions'
	directory, however, the file name may have a prefix of
	'product.', indicating that it should be found in a product
	directory.

	For example, if the module is: 'ACMEWidgets.foo', then an
	attempt will first be made to use the file
	'lib/python/Products/ACMEWidgets/Extensions/foo.py'. If this
	failes, then the file 'Extensions/ACMEWidgets.foo.py' will be
	used.
    """
    i=ExternalMethod(id,title,module,function)
    self._setObject(id,i)
    return self.manage_main(self,REQUEST)

class ExternalMethod(OFS.SimpleItem.Item, Persistent, Explicit,
		     AccessControl.Role.RoleManager):
    """Web-callable functions that encapsulate external python functions.

    The function is defined in an external file.  This file is treated
    like a module, but is not a module.  It is not imported directly,
    but is rather read and evaluated.  The file must reside in the
    'Extensions' subdirectory of the Principia installation, or in an
    'Extensions' subdirectory of a product directory.

    Due to the way ExternalMethods are loaded, it is not *currently*
    possible to use Python modules that reside in the 'Extensions'
    directory.  It is possible to load modules found in the
    'lib/python' directory of the Principia installation, or in
    packages that are in the 'lib/python' directory.

    """

    meta_type='External Method'
    icon='misc_/ExternalMethod/function_icon'
    func_defaults=()
    func_code=None
    
    manage_options=(
	{'label':'Properties', 'action':'manage_main'},
	{'label':'Try It', 'action':''},
	{'label':'Security', 'action':'manage_access'},
	)

    __ac_permissions__=(
    ('View management screens', ['manage_main','manage_tabs']),
    ('Change permissions', ['manage_access']),
    ('Change External Methods', ['manage_edit',]),
    ('View', ['__call__','']),
    )

    def __init__(self, id, title, module, function):
	self.id=id
	self.manage_edit(title, module, function)

    manage_main=HTMLFile('methodEdit', globals())
    def manage_edit(self, title, module, function, REQUEST=None):
	"""Change the external method

	See the description of manage_addExternalMethod for a
	descriotion of the arguments 'module' and 'function'.

	Note that calling 'manage_edit' causes the "module" to be
	effectively reloaded.  This is useful during debugging to see
	the effects of changes, but can lead to problems of functions
	rely on shared global data.
	"""
	self.title=title
	if module[-3:]=='.py': module=module[:-3]
	elif module[-4:]=='.py': module=module[:-4]
	self._module=module
	self._function=function
	self.getFunction(1,1)
	if REQUEST: return MessageDialog(
	    title  ='Changed %s' % self.id,
	    message='%s has been updated' % self.id,
	    action =REQUEST['URL1']+'/manage_main',
	    target ='manage_main')

    def getFunction(self, check=0, reload=0):

        f=getObject(self._module, self._function, reload)
	if hasattr(f,'im_func'): ff=f.im_func
	else: ff=f
	   
	if check:
	    # Check to make sure function signature is the same.
	    # Otherwise, we may end up causing an unwanted change.

	    if self.func_defaults != ff.func_defaults:
		self.func_defaults  = ff.func_defaults
	    
	    func_code=FuncCode(ff,f is not ff)
	    if func_code != self.func_code: self.func_code=func_code
    
	self._v_f=f

	return f

    def __call__(self, *args, **kw):
	"""Call an ExternalMethod

	Calling an External Method is roughly equivalent to calling
	the original actual function from Python.  Positional and
	keyword parameters can be passed as usual.  Note however that
	unlike the case of a normal Python method, the "self" argument
	must be passed explicitly.  An exception to this rule is made
	if:

	- The supplied number of arguments is one less than the
	  required number of arguments, and

        - The name of the function\'s first argument is 'self'.

	In this case, the URL parent of the object is supplied as the
	first argument.
	"""
	
	try: f=self._v_f
	except: f=self.getFunction()

	__traceback_info__=args, kw, self.func_defaults

	try:
	    try:
		try: return apply(f,args,kw)
		except TypeError, v:
		    tb=sys.exc_traceback
		    try:
			if ((self.func_code.co_argcount-
			     len(self.func_defaults or ()) - 1 == len(args))
			    and self.func_code.co_varnames[0]=='self'):
		            return apply(f,(self.aq_parent,)+args,kw)

			raise TypeError, v, tb
		    finally: tb=None
	    except:
		error_type=sys.exc_type
		error_value=sys.exc_value
		tb=sys.exc_traceback
		if lower(error_type) in ('redirect',):
		    raise error_type, error_value, tb
		if (type(error_value) is type('') and
		    regex.search('[a-zA-Z]>', error_value) > 0):
		    error_message=error_value
		else:
		    error_message=''
		error_tb=pretty_tb(error_type, error_value, tb)
		c=self.aq_parent
		try:
		    s=getattr(c, 'standard_error_message')
		    v=HTML.__call__(s, c, self.aq_acquire('REQUEST'),
				    error_type=error_type,
				    error_value=error_value,
				    error_tb=error_tb, error_traceback=error_tb,
				    error_message=error_message)
		except: v='Sorry, an error occured'
		raise error_type, v, tb
	finally: tb=None
		

    def function(self): return self._function
    def module(self): return self._module

import __init__
__init__.need_license=1


##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

__version__='$Revision$'[11:-2]

import Globals
from AccessControl import getSecurityManager
from AccessControl.ZopeGuards import guarded_getattr
from Persistence import Persistent
from string import join, strip
import re

defaultBindings = {'name_context': 'context',
                   'name_container': 'container',
                   'name_m_self': 'script',
                   'name_ns': '',
                   'name_subpath': 'traverse_subpath'}

_marker = []  # Create a new marker

class NameAssignments:
    # Note that instances of this class are intended to be immutable
    # and persistent but not inherit from ExtensionClass.

    _exprs = (('name_context',   'self._getContext()'),
              ('name_container', 'self._getContainer()'),
              ('name_m_self',    'self'),
              ('name_ns',        'self._getNamespace(caller_namespace, kw)'),
              ('name_subpath',   'self._getTraverseSubpath()'),
              )

    _isLegalName = re.compile(r'_$|[a-zA-Z][a-zA-Z0-9_]*$').match
    _asgns = {}

    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, mapping):
        # mapping is presumably the REQUEST or compatible equivalent.
        # Note that we take care not to store expression texts in the ZODB.
        asgns = {}
        _isLegalName = self._isLegalName
        for name, expr in self._exprs:
            if mapping.has_key(name):
                assigned_name = strip(mapping[name])
                if not assigned_name:
                    continue
                if not _isLegalName(assigned_name):
                    raise ValueError, ('"%s" is not a valid variable name.'
                                       % assigned_name)
                asgns[name] = assigned_name
        self._asgns = asgns

    def isAnyNameAssigned(self):
        if len(self._asgns) > 0:
            return 1
        return 0

    def isNameAssigned(self, name):
        return self._asgns.has_key(name)

    def getAssignedName(self, name, default=_marker):
        val = self._asgns.get(name, default)
        if val is _marker:
            raise KeyError, name
        return val

    def getAssignedNames(self):
        # Returns a copy of the assigned names mapping
        return self._asgns.copy()

    def getAssignedNamesInOrder(self):
        # Returns the assigned names in the same order as that of
        # self._exprs.
        rval = []
        asgns = self._asgns
        for name, expr in self._exprs:
            if asgns.has_key(name):
                assigned_name = asgns[name]
                rval.append(assigned_name)
        return rval

    def _generateCodeBlock(self, bindtext, assigned_names):
        # Returns a tuple: exec-able code that can compute the value of
        # the bindings and eliminate clashing keyword arguments,
        # and the number of names bound.
        text = ['bound_data.append(%s)\n' % bindtext]
        for assigned_name in assigned_names:
            text.append('if kw.has_key("%s"):\n' % assigned_name)
            text.append('    del kw["%s"]\n'     % assigned_name)
        codetext = join(text, '')
        return (compile(codetext, '<string>', 'exec'), len(assigned_names))

    def _createCodeBlockForMapping(self):
        # Generates a code block which generates the "bound_data"
        # variable and removes excessive arguments from the "kw"
        # variable.  bound_data will be a mapping, for use as a
        # global namespace.
        exprtext = []
        assigned_names = []
        asgns = self._asgns
        for name, expr in self._exprs:
            if asgns.has_key(name):
                assigned_name = asgns[name]
                assigned_names.append(assigned_name)
                exprtext.append('"%s":%s,' % (assigned_name, expr))
        text = '{%s}' % join(exprtext, '')
        return self._generateCodeBlock(text, assigned_names)

    def _createCodeBlockForTuple(self, argNames):
        # Generates a code block which generates the "bound_data"
        # variable and removes excessive arguments from the "kw"
        # variable.  bound_data will be a tuple, for use as
        # positional arguments.
        assigned_names = []
        exprtext = []
        asgns = self._asgns
        for argName in argNames:
            passedLastBoundArg = 1
            for name, expr in self._exprs:
                # Provide a value for the available exprs.
                if asgns.has_key(name):
                    assigned_name = asgns[name]
                    if assigned_name == argName:
                        # The value for this argument will be filled in.
                        exprtext.append('%s,' % expr)
                        assigned_names.append(assigned_name)
                        passedLastBoundArg = 0
                        break
            if passedLastBoundArg:
                # Found last of bound args.
                break
        text = '(%s)' % join(exprtext, '')
        return self._generateCodeBlock(text, assigned_names)


from AccessControl.unauthorized import Unauthorized

class UnauthorizedBinding:
    """Explanation: as of Zope 2.6.3 a security hole was closed - no
       security check was happening when 'context' and 'container'
       were bound to a script. Adding the check broke lots of sites
       where existing scripts had the container binding but the users
       of the scripts didn't have access to the container (e.g. workflow
       scripts). This meant getting unauthorized even if the container
       binding wasn't used in the script.

       Now, instead of raising unauthorized at binding time, we bind
       to an UnauthorizedBinding that will allow the script to run if
       it doesn't actually use the binding, but will raise a meaningful
       unauthorized error if the binding is accessed. This makes the
       backward compatibility problem less painful because only those
       actually using the container binding (for ex. workflow scripts)
       need to take explicit action to fix existing sites."""

    def __init__(self, name, wrapped):
        self._name = name
        self._wrapped = wrapped

    __allow_access_to_unprotected_subobjects__ = 1

    def __getattr__(self, name, default=None):

        # Make *extra* sure that the wrapper isn't used to access
        # __call__, __str__, __repr__, etc.
        if name.startswith('__'):
            self.__you_lose()

        return guarded_getattr(self._wrapped, name, default)

    def __you_lose(self):
        name = self.__dict__['_name']
        raise Unauthorized('Not authorized to access binding: %s' % name)

    __str__ = __call__ = index_html = __you_lose

class Bindings:

    __ac_permissions__ = (
        ('View management screens', ('getBindingAssignments',)),
        ('Change bindings', ('ZBindings_edit', 'ZBindings_setClient')),
        )

    _Bindings_client = None

    def ZBindings_edit(self, mapping):
        names = self._setupBindings(mapping)
        self._prepareBindCode()
        self._editedBindings()

    def ZBindings_setClient(self, clientname):
        '''Name the binding to be used as the "client".

        This is used by classes such as DTMLFile that want to
        choose an object on which to operate by default.'''
        self._Bindings_client = str(clientname)

    def _editedBindings(self):
        # Override to receive notification when the bindings are edited.
        pass

    def _setupBindings(self, names={}):
        self._bind_names = names = NameAssignments(names)
        return names

    def getBindingAssignments(self):
        if not hasattr(self, '_bind_names'):
            self._setupBindings()
        return self._bind_names

    def __before_publishing_traverse__(self, self2, request):
        path = request['TraversalRequestNameStack']
        names = self.getBindingAssignments()
        if (not names.isNameAssigned('name_subpath') or
            (path and hasattr(self.aq_base, path[-1])) ):
            return
        subpath = path[:]
        path[:] = []
        subpath.reverse()
        request.set('traverse_subpath', subpath)

    def _createBindCode(self, names):
        return names._createCodeBlockForMapping()

    def _prepareBindCode(self):
        # Creates:
        # - a code block that quickly generates "bound_data" and
        #   modifies the "kw" variable.
        # - a count of the bound arguments.
        # Saves them in _v_bindcode and _v_bindcount.
        # Returns .
        names = self.getBindingAssignments()
        if names.isAnyNameAssigned():
            bindcode, bindcount = self._createBindCode(names)
        else:
            bindcode, bindcount = None, 0
        self._v_bindcode = bindcode
        self._v_bindcount = bindcount
        return bindcode

    def _getBindCount(self):
        bindcount = getattr(self, '_v_bindcount', _marker)
        if bindcount is _marker:
            self._prepareBindCode()
            bindcount = self._v_bindcount
        return bindcount

    def _getContext(self):
        # Utility for bindcode.
        while 1:
            self = self.aq_parent
            if not getattr(self, '_is_wrapperish', None):
                parent = getattr(self, 'aq_parent', None)
                inner = getattr(self, 'aq_inner', None)
                container = getattr(inner, 'aq_parent', None)
                try: getSecurityManager().validate(parent, container, '', self)
                except Unauthorized:
                    return UnauthorizedBinding('context', self)
                return self

    def _getContainer(self):
        # Utility for bindcode.
        while 1:
            self = self.aq_inner.aq_parent
            if not getattr(self, '_is_wrapperish', None):
                parent = getattr(self, 'aq_parent', None)
                inner = getattr(self, 'aq_inner', None)
                container = getattr(inner, 'aq_parent', None)
                try: getSecurityManager().validate(parent, container, '', self)
                except Unauthorized:
                    return UnauthorizedBinding('container', self)
                return self

    def _getTraverseSubpath(self):
        # Utility for bindcode.
        if hasattr(self, 'REQUEST'):
            return self.REQUEST.other.get('traverse_subpath', [])
        else:
            return []

    def _getNamespace(self, caller_namespace, kw):
        # Utility for bindcode.
        if caller_namespace is None:
            # Try to get the caller's namespace by scanning
            # the keyword arguments for an argument with the
            # same name as the assigned name for name_ns.
            names = self.getBindingAssignments()
            assigned_name = names.getAssignedName('name_ns')
            caller_namespace = kw.get(assigned_name, None)
        if caller_namespace is None:
            # Create an empty namespace.
            return self._Bindings_ns_class()
        return caller_namespace

    def __call__(self, *args, **kw):
        '''Calls the script.'''
        return self._bindAndExec(args, kw, None)

    def __render_with_namespace__(self, namespace):
        '''Calls the script with the specified namespace.'''
        namevals = {}
        # Try to find unbound parameters in the namespace, if the
        # namespace is bound.
        if self.getBindingAssignments().isNameAssigned('name_ns'):
            code = self.func_code
            for name in code.co_varnames[:code.co_argcount]:
                try:
                    namevals[name] = namespace[name]
                except KeyError:
                    pass
        return self._bindAndExec((), namevals, namespace)

    render = __call__

    def _bindAndExec(self, args, kw, caller_namespace):
        '''Prepares the bound information and calls _exec(), possibly
        with a namespace.
        '''
        bindcode = getattr(self, '_v_bindcode', _marker)
        if bindcode is _marker:
            bindcode = self._prepareBindCode()

        # Execute the script in a new security context (including the
        # bindings preparation).
        security = getSecurityManager()
        security.addContext(self)
        try:
            if bindcode is None:
                bound_data = {}
            else:
                bound_data = []
                exec bindcode
                bound_data = bound_data[0]
            return self._exec(bound_data, args, kw)
        finally:
            security.removeContext(self)

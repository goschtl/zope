##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################
"""Database connection support

$Id: Connection.py,v 1.9 1999/06/24 19:33:12 jim Exp $"""
__version__='$Revision: 1.9 $'[11:-2]

from cPickleCache import PickleCache
from POSException import ConflictError, ExportError
from cStringIO import StringIO
from cPickle import Unpickler, Pickler
from ExtensionClass import Base
import Transaction, string, ExportImport, sys, traceback

ExtensionKlass=Base.__class__

class HelperClass: pass
ClassType=type(HelperClass)

class Connection(ExportImport.ExportImport):
    """Object managers for individual object space.

    An object space is a version of collection of objects.  In a
    multi-threaded application, each thread get's it's own object
    space.

    The Connection manages movement of objects in and out of object storage.
    """

    def __init__(self, storage, version='', cache_size=400,
                 cache_deactivate_after=60):
        """Create a new Connection"""
        self._storage=storage
        self.new_oid=storage.new_oid
        self._version=version
        self._cache=cache=PickleCache(self, cache_size, cache_deactivate_after)
        self._incrgc=cache.incrgc
        self._invalidated=d={}
        self._invalid=d.has_key
        self._committed=[]

    def _breakcr(self):
        try: del self._cache
        except: pass
        try: del self._incrgc
        except: pass

    def __getitem__(self, oid,
                    tt=type(()), ct=type(HelperClass)):
        cache=self._cache
        if cache.has_key(oid): return cache[oid]

        __traceback_info__=oid
        p, serial = self._storage.load(oid, self._version)
        file=StringIO(p)
        unpickler=Unpickler(file)
        unpickler.persistent_load=self._persistent_load

        object = unpickler.load()

        klass, args = object

        if type(klass) is tt:
            module, name = klass
            klass=self._db._classFactory(self, module, name)
        
        if (args is None or
            not args and not hasattr(klass,'__getinitargs__')):
            object=klass.__basicnew__()
        else:
            object=apply(klass,args)
            if klass is not ExtensionKlass:
                object.__dict__.clear()

        object._p_oid=oid
        object._p_jar=self
        object._p_changed=None
        object._p_serial=serial

        cache[oid]=object
        if oid=='\0\0\0\0\0\0\0\0': self._root_=object # keep a ref
        return object

    def _persistent_load(self,oid,
                        d={'__builtins__':{}},
                        tt=type(()), st=type(''), ct=type(HelperClass)):

        __traceback_info__=oid

        cache=self._cache

        if type(oid) is tt:
            # Quick instance reference.  We know all we need to know
            # to create the instance wo hitting the db, so go for it!
            oid, klass = oid
            if cache.has_key(oid): return cache[oid]

            if type(klass) is tt:
                module, name = klass
                try: klass=self._db._classFactory(self, module, name)
                except:
                    # Eek, we couldn't get the class. Hm.
                    # Maybe their's more current data in the
                    # object's actual record!
                    return self[oid]
            
            object=klass.__basicnew__()
            object._p_oid=oid
            object._p_jar=self
            object._p_changed=None
            
            cache[oid]=object

            return object

        if cache.has_key(oid): return cache[oid]
        return self[oid]

    def _planToStore(self,object,stackp):
        oid=object._p_oid
        if oid is None or object._p_jar is not self:
            oid = self.new_oid()
            object._p_jar=self
            object._p_oid=oid
            stackp(object)
            
        elif object._p_changed:
            stackp(object)

        return oid

    def _setDB(self, odb=None):
        """Begin a new transaction.

        Any objects modified since the last transaction are invalidated.
        """     
        self._db=odb
        self._cache.invalidate(self._invalidated)

        return self

    def abort(self, object, transaction):
        """Abort the object in the transaction.

        This just deactivates the thing.
        """
        del object._p_changed

    def close(self):
        self._incrgc()
        self._db._closeConnection(self)
        del self._db

    def commit(self, object, transaction):
        oid=object._p_oid
        invalid=self._invalid
        if invalid(oid) or invalid(None): raise ConflictError, oid
        self._invalidating.append(oid)
        plan=self._planToStore
        stack=[]
        stackup=stack.append
        topoid=plan(object,stackup)
        version=self._version

        if stack:
            # Create a special persistent_id that passes T and the subobject
            # stack along:
            def persistent_id(object,self=self,stackup=stackup):
                if (not hasattr(object, '_p_oid') or
                    type(object) is ClassType): return None

                oid=object._p_oid

                if oid is None or object._p_jar is not self:
                    oid = self.new_oid()
                    object._p_jar=self
                    object._p_oid=oid
                    stackup(object)

                klass=object.__class__

                if klass is ExtensionKlass: return oid
                
                if hasattr(klass, '__getinitargs__'): return oid

                try: module=klass.__module__
                except: module=''
                if module: klass=module, klass.__name__
                
                return oid, klass

            file=StringIO()
            seek=file.seek
            pickler=Pickler(file,1)
            pickler.persistent_id=persistent_id
            dbstore=self._storage.store
            file=file.getvalue
            cache=self._cache
            dump=pickler.dump
            clear_memo=pickler.clear_memo

            while stack:
                object=stack[-1]
                del stack[-1]
                oid=object._p_oid
                try: serial=object._p_serial
                except: serial='\0'*8
                if invalid(oid): raise ConflictError, oid
                klass = object.__class__

                if klass is ExtensionKlass:
                    # Yee Ha!
                    dict={}
                    dict.update(object.__dict__)
                    del dict['_p_jar']
                    args=object.__name__, object.__bases__, dict
                    state=None
                else:
                    if hasattr(klass, '__getinitargs__'):
                        args = object.__getinitargs__()
                        len(args) # XXX Assert it's a sequence
                    else:
                        args = None # New no-constructor protocol!

                    try: module=klass.__module__
                    except: module=''
                    if module: klass=module, klass.__name__
                    state=object.__getstate__()

                seek(0)
                clear_memo()
                dump((klass,args))
                dump(state)
                p=file()
                object._p_serial=dbstore(oid,serial,p,version,transaction)
                object._p_changed=0
                try: cache[oid]=object
                except:
                    # Dang, I bet its wrapped:
                    if hasattr(object, 'aq_base'):
                        cache[oid]=object.aq_base

        return topoid

    def db(self): return self._db

    def getVersion(self): return self._version
        
    def invalidate(self, oid):
        """Invalidate a particular oid

        This marks the oid as invalid, but doesn't actually invalidate
        it.  The object data will be actually invalidated at certain
        transaction boundaries.
        """
        self._invalidated[oid]=1

    def modifiedInVersion(self, o):
        return self._db.modifiedInVersion(o._p_oid)

    def root(self): return self['\0\0\0\0\0\0\0\0']

    def setstate(self,object):
        # Note, we no longer mess with the object's state
        # flag, _p_changed.  This is the object's job.
        oid=object._p_oid
        invalid=self._invalid
        if invalid(oid) or invalid(None): raise ConflictError, oid
        p, serial = self._storage.load(oid, self._version)
        file=StringIO(p)
        unpickler=Unpickler(file)
        unpickler.persistent_load=self._persistent_load
        try:
            unpickler.load()
            state = unpickler.load()
        except:
            t, v =sys.exc_info()[:2]
            raise
            
        if hasattr(object, '__setstate__'):
            object.__setstate__(state)
        else:
            d=object.__dict__
            for k,v in state.items(): d[k]=v
        object._p_serial=serial

    def tpc_abort(self, transaction):
        self._storage.tpc_abort(transaction)
        cache=self._cache
        cache.invalidate(self._invalidated)
        cache.invalidate(self._invalidating)

    def tpc_begin(self, transaction):
        if self._invalid(None): # Some nitwit invalidated everything!
            raise ConflictError, oid 
        self._invalidating=[]
        self._storage.tpc_begin(transaction)

    def tpc_finish(self, transaction):
        self._storage.tpc_finish(transaction, self.tpc_finish_)
        self._cache.invalidate(self._invalidated)

    def tpc_finish_(self):
        invalidate=self._db.invalidate
        for oid in self._invalidating: invalidate(oid, self)

class tConnection(Connection):

    def close(self):
        self._breakcr()


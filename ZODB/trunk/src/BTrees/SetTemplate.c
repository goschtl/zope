/*****************************************************************************
  
  Zope Public License (ZPL) Version 1.0
  -------------------------------------
  
  Copyright (c) Digital Creations.  All rights reserved.
  
  This license has been certified as Open Source(tm).
  
  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions are
  met:
  
  1. Redistributions in source code must retain the above copyright
     notice, this list of conditions, and the following disclaimer.
  
  2. Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions, and the following disclaimer in
     the documentation and/or other materials provided with the
     distribution.
  
  3. Digital Creations requests that attribution be given to Zope
     in any manner possible. Zope includes a "Powered by Zope"
     button that is installed by default. While it is not a license
     violation to remove this button, it is requested that the
     attribution remain. A significant investment has been put
     into Zope, and this effort will continue if the Zope community
     continues to grow. This is one way to assure that growth.
  
  4. All advertising materials and documentation mentioning
     features derived from or use of this software must display
     the following acknowledgement:
  
       "This product includes software developed by Digital Creations
       for use in the Z Object Publishing Environment
       (http://www.zope.org/)."
  
     In the event that the product being advertised includes an
     intact Zope distribution (with copyright and license included)
     then this clause is waived.
  
  5. Names associated with Zope or Digital Creations must not be used to
     endorse or promote products derived from this software without
     prior written permission from Digital Creations.
  
  6. Modified redistributions of any form whatsoever must retain
     the following acknowledgment:
  
       "This product includes software developed by Digital Creations
       for use in the Z Object Publishing Environment
       (http://www.zope.org/)."
  
     Intact (re-)distributions of any official Zope release do not
     require an external acknowledgement.
  
  7. Modifications are encouraged but must be packaged separately as
     patches to official Zope releases.  Distributions that do not
     clearly separate the patches from the original work must be clearly
     labeled as unofficial distributions.  Modifications which do not
     carry the name Zope may be packaged in any form, as long as they
     conform to all of the clauses above.
  
  
  Disclaimer
  
    THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
    EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
    PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
    CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
    SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
    LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
    USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
    ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
    OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
    OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
    SUCH DAMAGE.
  
  
  This software consists of contributions made by Digital Creations and
  many individuals on behalf of Digital Creations.  Specific
  attributions are listed in the accompanying credits file.
  
 ****************************************************************************/

static PyObject *
Set_insert(Bucket *self, PyObject *args)
{
  PyObject *key;
  int i;

  UNLESS (PyArg_ParseTuple(args, "O", &key)) return NULL;
  if ( (i=_bucket_set(self, key, Py_None, 1, 1, 0)) < 0) return NULL;
  return PyInt_FromLong(i);
}

static PyObject *
Set_update(Bucket *self, PyObject *args)
{
  PyObject *seq=0, *o, *t, *v, *tb;
  int i, n=0, ind;

  UNLESS(PyArg_ParseTuple(args, "|O:update", &seq)) return NULL;

  if (seq)
    {
      for (i=0; ; i++)
        {
          UNLESS (o=PySequence_GetItem(seq, i))
            {
              PyErr_Fetch(&t, &v, &tb);
              if (t != PyExc_IndexError)
                {
                  PyErr_Restore(t, v, tb);
                  return NULL;
                }
              Py_XDECREF(t);
              Py_XDECREF(v);
              Py_XDECREF(tb);
              break;
            }
          ind=_bucket_set(self, o, Py_None, 1, 1, 0);
          Py_DECREF(o);
          if (ind < 0) return NULL;
          n += ind;
        }
    }

  return PyInt_FromLong(n);
}

static PyObject *
Set_remove(Bucket *self, PyObject *args)
{
  PyObject *key;

  UNLESS (PyArg_ParseTuple(args, "O", &key)) return NULL;
  if (_bucket_set(self, key, NULL, 0, 1, 0) < 0) return NULL;

  Py_INCREF(Py_None);
  return Py_None;
}

static int
_set_setstate(Bucket *self, PyObject *args)
{
  PyObject *k, *items;
  Bucket *next=0;
  int i, l, copied=1;
  KEY_TYPE *keys;
  VALUE_TYPE *values;

  UNLESS (PyArg_ParseTuple(args, "O|O", &items, &next))
    return -1;

  if ((l=PyTuple_Size(items)) < 0) return -1;

  for (i=self->len; --i >= 0; )
    {
      DECREF_KEY(self->keys[i]);
    }
  self->len=0;

  if (self->next)
    {
      Py_DECREF(self->next);
      self->next=0;
    }
  
  if (l > self->size)
    {
      UNLESS (keys=PyRealloc(self->keys, sizeof(KEY_TYPE)*l)) return -1;
      self->keys=keys;
      self->size=l;
    }
  
  for (i=0; i<l; i++)
    {
      k=PyTuple_GET_ITEM(items, i);
      COPY_KEY_FROM_ARG(self->keys[i], k, &copied);
      UNLESS (copied) return -1;
      INCREF_KEY(self->keys[i]);
    }

  self->len=l;

  if (next)
    {
      self->next=next;
      Py_INCREF(next);
    }

  return 0;
}

static PyObject *
set_setstate(Bucket *self, PyObject *args)
{
  int r;

  UNLESS (PyArg_ParseTuple(args, "O", &args)) return NULL;

  PER_PREVENT_DEACTIVATION(self); 
  r=_set_setstate(self, args);
  PER_ALLOW_DEACTIVATION(self);

  if (r < 0) return NULL;
  Py_INCREF(Py_None);
  return Py_None;
}

static struct PyMethodDef Set_methods[] = {
  {"__getstate__", (PyCFunction) bucket_getstate,	METH_VARARGS,
   "__getstate__() -- Return the picklable state of the object"},
  {"__setstate__", (PyCFunction) set_setstate,	METH_VARARGS,
   "__setstate__() -- Set the state of the object"},
  {"keys",	(PyCFunction) bucket_keys,	METH_VARARGS,
     "keys() -- Return the keys"},
  {"has_key",	(PyCFunction) bucket_has_key,	METH_VARARGS,
     "has_key(key) -- Test whether the bucket contains the given key"},
  {"clear",	(PyCFunction) bucket_clear,	METH_VARARGS,
   "clear() -- Remove all of the items from the bucket"},
  {"maxKey", (PyCFunction) Bucket_maxKey,	METH_VARARGS,
   "maxKey([key]) -- Fine the maximum key\n\n"
   "If an argument is given, find the maximum <= the argument"},
  {"minKey", (PyCFunction) Bucket_minKey,	METH_VARARGS,
   "minKey([key]) -- Fine the minimum key\n\n"
   "If an argument is given, find the minimum >= the argument"},
#ifdef PERSISTENT
  {"_p_resolveConflict", (PyCFunction) bucket__p_resolveConflict, METH_VARARGS,
   "_p_resolveConflict() -- Reinitialize from a newly created copy"},
  {"_p_deactivate", (PyCFunction) bucket__p_deactivate, METH_VARARGS,
   "_p_deactivate() -- Reinitialize from a newly created copy"},
#endif
  {"insert",	(PyCFunction)Set_insert,	METH_VARARGS,
   "insert(id,[ignored]) -- Add a key to the set"},
  {"update",	(PyCFunction)Set_update,	METH_VARARGS,
   "update(seq) -- Add the items from the given sequence to the set"},
  {"__init__",	(PyCFunction)Set_update,	METH_VARARGS,
   "__init__(seq) -- Initialize with  the items from the given sequence"},
  {"remove",	(PyCFunction)Set_remove,	METH_VARARGS,
   "remove(id) -- Remove an id from the set"},

  {NULL,		NULL}		/* sentinel */
};

static PyObject *
set_repr(Bucket *self)
{
  static PyObject *format;
  PyObject *r, *t;

  UNLESS (format) UNLESS (format=PyString_FromString(MOD_NAME_PREFIX "Set(%s)")) 
    return NULL;
  UNLESS (t=PyTuple_New(1)) return NULL;
  UNLESS (r=bucket_keys(self,NULL)) goto err;
  PyTuple_SET_ITEM(t,0,r);
  r=t;
  ASSIGN(r,PyString_Format(format,r));
  return r;
err:
  Py_DECREF(t);
  return NULL;
}

static int
set_length(Bucket *self) 
{
  int r;

  PER_USE_OR_RETURN(self, -1);
  r = self->len;
  PER_ALLOW_DEACTIVATION(self);

  return r;
}

static PyObject *
set_item(Bucket *self, int index)
{
  PyObject *r=0;

  PER_USE_OR_RETURN(self, NULL);
  if (index >= 0 && index < self->len)
    {
      COPY_KEY_TO_OBJECT(r, self->keys[index]);
    }
  else
    IndexError(index);

  PER_ALLOW_DEACTIVATION(self);

  return r;
}

static PySequenceMethods set_as_sequence = {
	(inquiry)set_length,		/*sq_length*/
	(binaryfunc)0,		/*sq_concat*/
	(intargfunc)0,		/*sq_repeat*/
	(intargfunc)set_item,		/*sq_item*/
	(intintargfunc)0,		/*sq_slice*/
	(intobjargproc)0,	/*sq_ass_item*/
	(intintobjargproc)0,	/*sq_ass_slice*/
};

static PyExtensionClass SetType = {
  PyObject_HEAD_INIT(NULL)
  0,				/*ob_size*/
  MOD_NAME_PREFIX "Set",			/*tp_name*/
  sizeof(Bucket),		/*tp_basicsize*/
  0,				/*tp_itemsize*/
  /*********** methods ***********************/
  (destructor) Bucket_dealloc,	/*tp_dealloc*/
  (printfunc)0,			/*tp_print*/
  (getattrfunc)0,		/*obsolete tp_getattr*/
  (setattrfunc)0,		/*obsolete tp_setattr*/
  (cmpfunc)0,			/*tp_compare*/
  (reprfunc) set_repr,		/*tp_repr*/
  0,				/*tp_as_number*/
  &set_as_sequence,		/*tp_as_sequence*/
  0,		                /*tp_as_mapping*/
  (hashfunc)0,			/*tp_hash*/
  (ternaryfunc)0,		/*tp_call*/
  (reprfunc)0,			/*tp_str*/
  (getattrofunc)0,		/*tp_getattro*/
  0,				/*tp_setattro*/
  
  /* Space for future expansion */
  0L,0L,
  "Set implemented as sorted keys", 
  METHOD_CHAIN(Set_methods),
  EXTENSIONCLASS_BASICNEW_FLAG 
#ifdef PERSISTENT
  | PERSISTENT_TYPE_FLAG 
#endif
  | EXTENSIONCLASS_NOINSTDICT_FLAG,
};

static int 
nextSet(SetIteration *i)
{
  UNLESS(PER_USE(BUCKET(i->set))) return -1;
          
  if (i->position >= 0)
    {
      if (i->position)
        {
          DECREF_KEY(i->key);
        }

      if (i->position < BUCKET(i->set)->len)
        {
          COPY_KEY(i->key, BUCKET(i->set)->keys[i->position]);
          INCREF_KEY(i->key);
          i->position ++;
        }
      else
        i->position = -1;
    }

  PER_ALLOW_DEACTIVATION(BUCKET(i->set));
          
  return 0;
}

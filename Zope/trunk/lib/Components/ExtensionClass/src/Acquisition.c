/*

  Copyright (c) 1996-1998, Digital Creations, Fredericksburg, VA, USA.  
  All rights reserved.
  
  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions are
  met:
  
    o Redistributions of source code must retain the above copyright
      notice, this list of conditions, and the disclaimer that follows.
  
    o Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions, and the following disclaimer in
      the documentation and/or other materials provided with the
      distribution.
  
    o Neither the name of Digital Creations nor the names of its
      contributors may be used to endorse or promote products derived
      from this software without specific prior written permission.
  
  
  THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS AND CONTRIBUTORS *AS
  IS* AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
  TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
  PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL
  CREATIONS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
  OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
  TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
  USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
  DAMAGE.

  $Id: Acquisition.c,v 1.52 2001/07/03 19:38:20 matt Exp $

  If you have questions regarding this software,
  contact:
 
    Digital Creations L.C.  
    info@digicool.com
 
    (540) 371-6909

*/
#include "ExtensionClass.h"

#define _IN_ACQUISITION_C
#include "Acquisition.h"

static ACQUISITIONCAPI AcquisitionCAPI;

static void
PyVar_Assign(PyObject **v,  PyObject *e)
{
  Py_XDECREF(*v);
  *v=e;
}

#define ASSIGN(V,E) PyVar_Assign(&(V),(E))
#define UNLESS(E) if (!(E))
#define UNLESS_ASSIGN(V,E) ASSIGN(V,E); UNLESS(V)
#define OBJECT(O) ((PyObject*)(O))

static PyObject *py__add__, *py__sub__, *py__mul__, *py__div__,
  *py__mod__, *py__pow__, *py__divmod__, *py__lshift__, *py__rshift__,
  *py__and__, *py__or__, *py__xor__, *py__coerce__, *py__neg__,
  *py__pos__, *py__abs__, *py__nonzero__, *py__invert__, *py__int__,
  *py__long__, *py__float__, *py__oct__, *py__hex__,
  *py__getitem__, *py__setitem__, *py__delitem__,
  *py__getslice__, *py__setslice__, *py__delslice__,
  *py__len__, *py__of__, *py__call__, *py__repr__, *py__str__, *py__cmp__;

static PyObject *Acquired=0;

static void
init_py_names(void)
{
#define INIT_PY_NAME(N) py ## N = PyString_FromString(#N)
  INIT_PY_NAME(__add__);
  INIT_PY_NAME(__sub__);
  INIT_PY_NAME(__mul__);
  INIT_PY_NAME(__div__);
  INIT_PY_NAME(__mod__);
  INIT_PY_NAME(__pow__);
  INIT_PY_NAME(__divmod__);
  INIT_PY_NAME(__lshift__);
  INIT_PY_NAME(__rshift__);
  INIT_PY_NAME(__and__);
  INIT_PY_NAME(__or__);
  INIT_PY_NAME(__xor__);
  INIT_PY_NAME(__coerce__);
  INIT_PY_NAME(__neg__);
  INIT_PY_NAME(__pos__);
  INIT_PY_NAME(__abs__);
  INIT_PY_NAME(__nonzero__);
  INIT_PY_NAME(__invert__);
  INIT_PY_NAME(__int__);
  INIT_PY_NAME(__long__);
  INIT_PY_NAME(__float__);
  INIT_PY_NAME(__oct__);
  INIT_PY_NAME(__hex__);
  INIT_PY_NAME(__getitem__);
  INIT_PY_NAME(__setitem__);
  INIT_PY_NAME(__delitem__);
  INIT_PY_NAME(__getslice__);
  INIT_PY_NAME(__setslice__);
  INIT_PY_NAME(__delslice__);
  INIT_PY_NAME(__len__);
  INIT_PY_NAME(__of__);
  INIT_PY_NAME(__call__);
  INIT_PY_NAME(__repr__);
  INIT_PY_NAME(__str__);
  INIT_PY_NAME(__cmp__);
  
#undef INIT_PY_NAME
}

static PyObject *
CallMethodO(PyObject *self, PyObject *name,
		     PyObject *args, PyObject *kw)
{
  if (! args && PyErr_Occurred()) return NULL;
  UNLESS(name=PyObject_GetAttr(self,name)) {
    if (args) { Py_DECREF(args); }
    return NULL;
  }
  ASSIGN(name,PyEval_CallObjectWithKeywords(name,args,kw));
  if (args) { Py_DECREF(args); }
  return name;
}

#define Build Py_BuildValue

/* Declarations for objects of type Wrapper */

typedef struct {
  PyObject_HEAD
  PyObject *obj;
  PyObject *container;
} Wrapper;

staticforward PyExtensionClass Wrappertype, XaqWrappertype;

#define isWrapper(O) ((O)->ob_type==(PyTypeObject*)&Wrappertype || \
		      (O)->ob_type==(PyTypeObject*)&XaqWrappertype)
#define WRAPPER(O) ((Wrapper*)(O))

static PyObject *
Wrapper__init__(Wrapper *self, PyObject *args)
{
  PyObject *obj, *container;

  UNLESS(PyArg_Parse(args,"(OO)",&obj,&container)) return NULL;
  Py_INCREF(obj);
  Py_INCREF(container);
  self->obj=obj;
  self->container=container;
  Py_INCREF(Py_None);
  return Py_None;
}

/* ---------------------------------------------------------------- */

static PyObject *
__of__(PyObject *inst, PyObject *parent)
{
  PyObject *r, *t;

  UNLESS(r=PyObject_GetAttr(inst, py__of__)) return NULL;
  UNLESS(t=PyTuple_New(1)) goto err;
  PyTuple_SET_ITEM(t,0,parent);
  ASSIGN(r,PyObject_CallObject(r,t));
  PyTuple_SET_ITEM(t,0,NULL);
  Py_DECREF(t);

  if (r 
      && r->ob_refcnt==1
      && isWrapper(r) 
      && WRAPPER(r)->container && isWrapper(WRAPPER(r)->container)
      )
    while (WRAPPER(r)->obj && isWrapper(WRAPPER(r)->obj)
	   && (WRAPPER(WRAPPER(r)->obj)->container == 
	       WRAPPER(WRAPPER(r)->container)->obj)
	   )
      {
	/* Simplify wrapper */
	Py_XINCREF(WRAPPER(WRAPPER(r)->obj)->obj);
	ASSIGN(WRAPPER(r)->obj, WRAPPER(WRAPPER(r)->obj)->obj);
      }

  return r;
err:
  Py_DECREF(r);
  return NULL;
}

static Wrapper *freeWrappers=0;
static int nWrappers=0;
#define MAX_CACHED_WRAPPERS 200

static PyObject *
newWrapper(PyObject *obj, PyObject *container, PyTypeObject *Wrappertype)
{
  Wrapper *self;
  
  if (freeWrappers)
    {
      self=freeWrappers;
      freeWrappers=(Wrapper*)self->obj;
      self->ob_type=Wrappertype;
      self->ob_refcnt=1;
      nWrappers--;
    }
  else
    {
      UNLESS(self = PyObject_NEW(Wrapper, Wrappertype)) return NULL;
    }

  Py_INCREF(Wrappertype);
  Py_XINCREF(obj);
  Py_XINCREF(container);
  self->obj=obj;
  self->container=container;
  return OBJECT(self);
}


static void
Wrapper_dealloc(Wrapper *self)     
{
  Py_XDECREF(self->obj);
  Py_XDECREF(self->container);
  Py_DECREF(self->ob_type);

  if (nWrappers < MAX_CACHED_WRAPPERS)
    {
      self->obj=OBJECT(freeWrappers);
      freeWrappers=self;
      nWrappers++;
    }
  else 
    {
      PyMem_DEL(self);
    }
}

static PyObject *
Wrapper_special(Wrapper *self, char *name, PyObject *oname)
{
  PyObject *r=0;

  switch(*name)
    {
    case 'b':
      if (strcmp(name,"base")==0)
	{
	  if (self->obj)
	    {
	      r=self->obj;
	      while (isWrapper(r) && WRAPPER(r)->obj) r=WRAPPER(r)->obj;
	    }
	  else r=Py_None;
	  Py_INCREF(r);
	  return r;
	}
      break;
    case 'p':
      if (strcmp(name,"parent")==0)
	{
	  if (self->container) r=self->container;
	  else r=Py_None;
	  Py_INCREF(r);
	  return r;
	}
      break;
    case 's':
      if (strcmp(name,"self")==0)
	{
	  if (self->obj) r=self->obj;
	  else r=Py_None;
	  Py_INCREF(r);
	  return r;
	}
      break;
    case 'e':
      if (strcmp(name,"explicit")==0)
	{
	  if (self->ob_type != (PyTypeObject *)&XaqWrappertype)
	    return newWrapper(self->obj, self->container, 
			      (PyTypeObject *)&XaqWrappertype);
	  Py_INCREF(self);
	  return OBJECT(self);
	}
      break;
    case 'a':
      if (strcmp(name,"acquire")==0)
	{
	  return Py_FindAttr(OBJECT(self),oname);
	}
      break;
    case 'c':
      if (strcmp(name,"chain")==0)
	{
	  if ((r = PyList_New(0)))
	    while (1)
	      {
		if (PyList_Append(r,OBJECT(self)) >= 0)
		  {
		    if (isWrapper(self) && self->container) 
		      {
			self=WRAPPER(self->container);
			continue;
		      }
		  }
		else
		  {
		    Py_DECREF(r);
		  }
		break;
	      }
	  return r;
	}
      break;
    case 'i':
      if (strcmp(name,"inContextOf")==0)
	{
	  return Py_FindAttr(OBJECT(self),oname);
	}
      if (strcmp(name,"inner")==0)
	{
	  if (self->obj)
	    {
	      r=self->obj;
	      while (isWrapper(r) && WRAPPER(r)->obj) 
		{
		  self=WRAPPER(r);
		  r=WRAPPER(r)->obj;
		}
	      r=OBJECT(self);
	    }
	  else r=Py_None;

	  Py_INCREF(r);
	  return r;
	}
      break;

    case 'u':
      if (strcmp(name,"uncle")==0)
	{
	  return PyString_FromString("Bob");
	}
      break;
      
    }

  return NULL;
}

static int
apply_filter(PyObject *filter, PyObject *inst, PyObject *oname, PyObject *r,
	     PyObject *extra, PyObject *orig)
{
  PyObject *fr;
  int ir;

  UNLESS(fr=PyTuple_New(5)) goto err;
  PyTuple_SET_ITEM(fr,0,orig);
  Py_INCREF(orig);
  PyTuple_SET_ITEM(fr,1,inst);
  Py_INCREF(inst);
  PyTuple_SET_ITEM(fr,2,oname);
  Py_INCREF(oname);
  PyTuple_SET_ITEM(fr,3,r);
  Py_INCREF(r);
  PyTuple_SET_ITEM(fr,4,extra);
  Py_INCREF(extra);
  UNLESS_ASSIGN(fr,PyObject_CallObject(filter, fr)) goto err;
  ir=PyObject_IsTrue(fr);
  Py_DECREF(fr);
  if (ir) return 1;
  Py_DECREF(r);
  return 0;
err:
  Py_DECREF(r);
  return -1;
}

static PyObject *
Wrapper_acquire(Wrapper *self, PyObject *oname, 
		PyObject *filter, PyObject *extra, PyObject *orig,
		int explicit, int containment);

static PyObject *
Wrapper_findattr(Wrapper *self, PyObject *oname,
		PyObject *filter, PyObject *extra, PyObject *orig,
		int sob, int sco, int explicit, int containment)
{
  PyObject *r, *v, *tb;
  char *name="";

  if (PyString_Check(oname)) name=PyString_AS_STRING(oname);
  if (*name=='a' && name[1]=='q' && name[2]=='_')
    if ((r=Wrapper_special(self, name+3, oname)))
      {
	if (filter)
	  switch(apply_filter(filter,OBJECT(self),oname,r,extra,orig))
	    {
	    case -1: return NULL;
	    case 1: return r;
	    }
	else return r;
      }
    else PyErr_Clear();
  else if (*name=='_' && name[1]=='_' && strcmp(name+2,"reduce__")==0)
    {
      PyErr_SetString(PyExc_TypeError, 
                      "Can't pickle objects in acquisition wrappers.");
      return NULL;
    }

  /* If we are doing a containment search, then replace self with aq_inner */
  if (containment)
    while (self->obj && isWrapper(self->obj))
      self=WRAPPER(self->obj);

  if (sob && self->obj)
    {
      if (isWrapper(self->obj))
	{
	  if ((r=Wrapper_findattr(WRAPPER(self->obj),
				 oname, filter, extra, orig, 1, 

				 /* Search object container if explicit,
				    or object is implicit acquirer */
				 explicit ||
				 self->obj->ob_type == 
				 (PyTypeObject*)&Wrappertype,
				  explicit, containment)))
	    {
	      if (PyECMethod_Check(r) && PyECMethod_Self(r)==self->obj)
		ASSIGN(r,PyECMethod_New(r,OBJECT(self)));
	      else if (has__of__(r)) ASSIGN(r,__of__(r,OBJECT(self)));
	      return r;
	    }

	  PyErr_Fetch(&r,&v,&tb);
	  if (r && (r != PyExc_AttributeError))
	    {
	      PyErr_Restore(r,v,tb);
	      return NULL;
	    }
	  Py_XDECREF(r); Py_XDECREF(v); Py_XDECREF(tb);
	  r=NULL;
	}
      else if ((r=PyObject_GetAttr(self->obj,oname)))
	{
	  if (r==Acquired)
	    {
	      Py_DECREF(r);
	      return Wrapper_acquire(self, oname, filter, extra, orig, 1, 
				     containment);
	    }

	  if (PyECMethod_Check(r) && PyECMethod_Self(r)==self->obj)
	    ASSIGN(r,PyECMethod_New(r,OBJECT(self)));
	  else if (has__of__(r)) ASSIGN(r,__of__(r,OBJECT(self)));

	  if (filter)
	    switch(apply_filter(filter,OBJECT(self),oname,r,extra,orig))
	      {
	      case -1: return NULL;
	      case 1: return r;
	      }
	  else return r;
	}
      else {
	PyErr_Fetch(&r,&v,&tb);
	if (r != PyExc_AttributeError)
	  {
	    PyErr_Restore(r,v,tb);
	    return NULL;
	  }
	Py_XDECREF(r); Py_XDECREF(v); Py_XDECREF(tb);
	r=NULL;
      }
      PyErr_Clear();
    }

  if (sco && (*name != '_' || explicit)) 
    return Wrapper_acquire(self, oname, filter, extra, orig, explicit, 
			   containment);

  PyErr_SetObject(PyExc_AttributeError,oname);
  return NULL;
}

static PyObject *
Wrapper_acquire(Wrapper *self, PyObject *oname, 
		PyObject *filter, PyObject *extra, PyObject *orig,
		int explicit, int containment)
{
  PyObject *r;
  int sob=1, sco=1;

  if (self->container)
    {
      if (isWrapper(self->container))
	{
	  if (self->obj && isWrapper(self->obj))
	    {
	      /* Try to optimize search by recognizing repeated obs in path */
	      if (WRAPPER(self->obj)->container==
		  WRAPPER(self->container)->container) 
		sco=0;
	      else if (WRAPPER(self->obj)->container==
		      WRAPPER(self->container)->obj)  
		sob=0;
	   }

	  r=Wrapper_findattr((Wrapper*)self->container,
			     oname, filter, extra, orig, sob, sco, explicit, 
			     containment);
	  
	  if (r && has__of__(r)) ASSIGN(r,__of__(r,OBJECT(self)));
	  return r;
	}
      else
	{
	  if ((r=PyObject_GetAttr(self->container,oname))) {
	    if (r == Acquired)
	      {
		Py_DECREF(r);
	      }
	    else {
	      if (filter)
		switch(apply_filter(filter,self->container,oname,r,
				    extra,orig))
		  {
		  case -1: 
		    return NULL;
		  case 1: 
		    if (has__of__(r)) ASSIGN(r,__of__(r,OBJECT(self)));
		    return r;
		  }
	      else 
		{
		  if (has__of__(r)) ASSIGN(r,__of__(r,OBJECT(self)));
		  return r;
		}
	    }
	  }
	}
    }
  
  PyErr_SetObject(PyExc_AttributeError, oname);
  return NULL;
}

static PyObject *
Wrapper_getattro(Wrapper *self, PyObject *oname)
{
  if (self->obj || self->container)
    return Wrapper_findattr(self, oname, NULL, NULL, NULL, 1, 1, 0, 0);

  /* Maybe we are getting initialized? */
  return Py_FindAttr(OBJECT(self),oname);
}

static PyObject *
Xaq_getattro(Wrapper *self, PyObject *oname)
{
  char *name="";

  /* Special case backward-compatible acquire method. */
  if (PyString_Check(oname)) name=PyString_AS_STRING(oname);
  if (*name=='a' && name[1]=='c' && strcmp(name+2,"quire")==0)
    return Py_FindAttr(OBJECT(self),oname);

  if (self->obj || self->container)
    return Wrapper_findattr(self, oname, NULL, NULL, NULL, 1, 0, 0, 0);

  /* Maybe we are getting initialized? */
  return Py_FindAttr(OBJECT(self),oname);
}

static int
Wrapper_setattro(Wrapper *self, PyObject *oname, PyObject *v)
{
  char *name="";

  /* Allow assignment to parent, to change context. */
  if (PyString_Check(oname)) name=PyString_AS_STRING(oname);
  if (*name=='a' && name[1]=='q' && name[2]=='_' 
      && strcmp(name+3,"parent")==0)
    {
      Py_XINCREF(v);
      ASSIGN(self->container, v);
      return 0;
    }

  if (self->obj)
    {
      /* Unwrap passed in wrappers! */
      while (v && isWrapper(v))
	v=WRAPPER(v)->obj;

      if (v) return PyObject_SetAttr(self->obj, oname, v);
      else   return PyObject_DelAttr(self->obj, oname);
    }

  PyErr_SetString(PyExc_AttributeError, 
		  "Attempt to set attribute on empty acquisition wrapper");
  return -1;
}

static int
Wrapper_compare(Wrapper *self, PyObject *w)
{
  PyObject *obj, *wobj;
  PyObject *m;
  int r;

  if (OBJECT(self) == w) return 0;

  UNLESS (m=PyObject_GetAttr(OBJECT(self), py__cmp__))
    {
      /* Unwrap self completely -> obj. */
      while (self->obj && isWrapper(self->obj))
        self=WRAPPER(self->obj);
      obj = self->obj;
      /* Unwrap w completely -> wobj. */
      if (isWrapper(w))
        {
          while (WRAPPER(w)->obj && isWrapper(WRAPPER(w)->obj))
            w=WRAPPER(w)->obj;
          wobj = WRAPPER(w)->obj;
        }
      else wobj = w;

      PyErr_Clear();
      if (obj == wobj) return 0;
      return (obj < w) ? -1 : 1;
    }

  ASSIGN(m, PyObject_CallFunction(m, "O", w));
  UNLESS (m) return -1;
  
  r=PyInt_AsLong(m);

  Py_DECREF(m);

  return r;  
}

static PyObject *
Wrapper_repr(Wrapper *self)
{
  PyObject *r;

  if ((r=PyObject_GetAttr(OBJECT(self),py__repr__)))
    {
      ASSIGN(r,PyObject_CallFunction(r,NULL,NULL));
      return r;
    }
  else
    {
      PyErr_Clear();
      return PyObject_Repr(self->obj);
    }
}

static PyObject *
Wrapper_str(Wrapper *self)
{
  PyObject *r;

  if ((r=PyObject_GetAttr(OBJECT(self),py__str__)))
    {
      ASSIGN(r,PyObject_CallFunction(r,NULL,NULL));
      return r;
    }
  else
    {
      PyErr_Clear();
      return PyObject_Str(self->obj);
    }
}

static long
Wrapper_hash(Wrapper *self)
{
  return PyObject_Hash(self->obj);
}

static PyObject *
Wrapper_call(Wrapper *self, PyObject *args, PyObject *kw)
{
  Py_INCREF(args);
  return CallMethodO(OBJECT(self),py__call__,args,kw);
}

/* Code to handle accessing Wrapper objects as sequence objects */

static int
Wrapper_length(Wrapper *self)
{
  long l;
  PyObject *r;

  UNLESS(r=PyObject_GetAttr(OBJECT(self), py__len__)) return -1;
  UNLESS_ASSIGN(r,PyObject_CallObject(r,NULL)) return -1;
  l=PyInt_AsLong(r);
  Py_DECREF(r);
  return l;
}

static PyObject *
Wrapper_add(Wrapper *self, PyObject *bb)
{
  return CallMethodO(OBJECT(self),py__add__,Build("(O)", bb) ,NULL);
}

static PyObject *
Wrapper_mul(Wrapper *self, int  n)
{
  return CallMethodO(OBJECT(self),py__mul__,Build("(i)", n),NULL);
}

static PyObject *
Wrapper_item(Wrapper *self, int  i)
{
  return CallMethodO(OBJECT(self),py__getitem__, Build("(i)", i),NULL);
}

static PyObject *
Wrapper_slice(Wrapper *self, int  ilow, int  ihigh)
{
  return CallMethodO(OBJECT(self),py__getslice__,
		     Build("(ii)", ilow, ihigh),NULL);
}

static int
Wrapper_ass_item(Wrapper *self, int  i, PyObject *v)
{
  if (v)
    {
      UNLESS(v=CallMethodO(OBJECT(self),py__setitem__,
			   Build("(iO)", i, v),NULL))
	return -1;
    }
  else
    {
      UNLESS(v=CallMethodO(OBJECT(self),py__delitem__,
			   Build("(i)", i),NULL))
	return -1;
    }
  Py_DECREF(v);
  return 0;
}

static int
Wrapper_ass_slice(Wrapper *self, int  ilow, int  ihigh, PyObject *v)
{
  if (v)
    {
      UNLESS(v=CallMethodO(OBJECT(self),py__setslice__,
			   Build("(iiO)", ilow, ihigh, v),NULL))
	return -1;
    }
  else
    {
      UNLESS(v=CallMethodO(OBJECT(self),py__delslice__,
			   Build("(ii)", ilow, ihigh),NULL))
	return -1;
    }
  Py_DECREF(v);
  return 0;
}

static PySequenceMethods Wrapper_as_sequence = {
	(inquiry)Wrapper_length,		/*sq_length*/
	(binaryfunc)Wrapper_add,		/*sq_concat*/
	(intargfunc)Wrapper_mul,		/*sq_repeat*/
	(intargfunc)Wrapper_item,		/*sq_item*/
	(intintargfunc)Wrapper_slice,		/*sq_slice*/
	(intobjargproc)Wrapper_ass_item,	/*sq_ass_item*/
	(intintobjargproc)Wrapper_ass_slice,	/*sq_ass_slice*/
};

/* -------------------------------------------------------------- */

/* Code to access Wrapper objects as mappings */

static PyObject *
Wrapper_subscript(Wrapper *self, PyObject *key)
{
  return CallMethodO(OBJECT(self),py__getitem__,Build("(O)", key),NULL);
}

static int
Wrapper_ass_sub(Wrapper *self, PyObject *key, PyObject *v)
{
  if (v)
    {
      UNLESS(v=CallMethodO(OBJECT(self),py__setitem__,
			   Build("(OO)", key, v),NULL))
	return -1;
    }
  else
    {
      UNLESS(v=CallMethodO(OBJECT(self),py__delitem__,
			   Build("(O)", key),NULL))
	return -1;
    }
  Py_XDECREF(v);
  return 0;
}

static PyMappingMethods Wrapper_as_mapping = {
  (inquiry)Wrapper_length,		/*mp_length*/
  (binaryfunc)Wrapper_subscript,	/*mp_subscript*/
  (objobjargproc)Wrapper_ass_sub,	/*mp_ass_subscript*/
};

/* -------------------------------------------------------------- */

/* Code to access Wrapper objects as numbers */

static PyObject *
Wrapper_sub(Wrapper *self, PyObject *o)
{
  return CallMethodO(OBJECT(self),py__sub__,Build("(O)", o),NULL);
}

static PyObject *
Wrapper_div(Wrapper *self, PyObject *o)
{
  return CallMethodO(OBJECT(self),py__div__,Build("(O)", o),NULL);
}

static PyObject *
Wrapper_mod(Wrapper *self, PyObject *o)
{
  return CallMethodO(OBJECT(self),py__mod__,Build("(O)", o),NULL);
}

static PyObject *
Wrapper_divmod(Wrapper *self, PyObject *o)
{
  return CallMethodO(OBJECT(self),py__divmod__,Build("(O)", o),NULL);
}

static PyObject *
Wrapper_pow(Wrapper *self, PyObject *o, PyObject *m)
{
  return CallMethodO(OBJECT(self),py__pow__,Build("(OO)", o, m),NULL);
}

static PyObject *
Wrapper_neg(Wrapper *self)
{
  return CallMethodO(OBJECT(self), py__neg__, NULL, NULL);
}

static PyObject *
Wrapper_pos(Wrapper *self)
{
  return CallMethodO(OBJECT(self), py__pos__, NULL, NULL);
}

static PyObject *
Wrapper_abs(Wrapper *self)
{
  return CallMethodO(OBJECT(self), py__abs__, NULL, NULL);
}

static PyObject *
Wrapper_invert(Wrapper *self)
{
  return CallMethodO(OBJECT(self), py__invert__, NULL, NULL);
}

static PyObject *
Wrapper_lshift(Wrapper *self, PyObject *o)
{
  return CallMethodO(OBJECT(self),py__lshift__,Build("(O)", o),NULL);
}

static PyObject *
Wrapper_rshift(Wrapper *self, PyObject *o)
{
  return CallMethodO(OBJECT(self),py__rshift__,Build("(O)", o),NULL);
}

static PyObject *
Wrapper_and(Wrapper *self, PyObject *o)
{
  return CallMethodO(OBJECT(self),py__and__,Build("(O)", o),NULL);
}

static PyObject *
Wrapper_xor(Wrapper *self, PyObject *o)
{
  return CallMethodO(OBJECT(self),py__xor__,Build("(O)", o),NULL);
}

static PyObject *
Wrapper_or(Wrapper *self, PyObject *o)
{
  return CallMethodO(OBJECT(self),py__or__,Build("(O)", o),NULL);
}

static int 
Wrapper_coerce(Wrapper **self, PyObject **o)
{
  PyObject *m;

  UNLESS (m=PyObject_GetAttr(OBJECT(*self), py__coerce__))
    {
      PyErr_Clear();
      Py_INCREF(*self);
      Py_INCREF(*o);
      return 0;
    }

  ASSIGN(m, PyObject_CallFunction(m, "O", *o));
  UNLESS (m) return -1;

  UNLESS (PyArg_ParseTuple(m,"OO", self, o)) goto err;
  Py_INCREF(*self);
  Py_INCREF(*o);
  Py_DECREF(m);
  return 0;

err:
  Py_DECREF(m);
  return -1;  
}

static PyObject *
Wrapper_int(Wrapper *self)
{
  return CallMethodO(OBJECT(self), py__int__, NULL, NULL);
}

static PyObject *
Wrapper_long(Wrapper *self)
{
  return CallMethodO(OBJECT(self), py__long__, NULL, NULL);
}

static PyObject *
Wrapper_float(Wrapper *self)
{
  return CallMethodO(OBJECT(self), py__float__, NULL, NULL);
}

static PyObject *
Wrapper_oct(Wrapper *self)
{
  return CallMethodO(OBJECT(self), py__oct__, NULL, NULL);
}

static PyObject *
Wrapper_hex(Wrapper *self)
{
  return CallMethodO(OBJECT(self), py__hex__, NULL, NULL);
}

static int
Wrapper_nonzero(Wrapper *self)
{
  long l;
  PyObject *r;

  UNLESS(r=PyObject_GetAttr(OBJECT(self), py__nonzero__))
    {
      PyErr_Clear();

      /* Try len */
      UNLESS(r=PyObject_GetAttr(OBJECT(self), py__len__))
      {
        /* No len, it's true :-) */
        PyErr_Clear();
        return 1;
      }
    }

  UNLESS_ASSIGN(r,PyObject_CallObject(r,NULL)) return -1;
  l=PyInt_AsLong(r);
  Py_DECREF(r);
  return l;
}

static PyNumberMethods Wrapper_as_number = {
	(binaryfunc)Wrapper_add,	/*nb_add*/
	(binaryfunc)Wrapper_sub,	/*nb_subtract*/
	(binaryfunc)Wrapper_mul,	/*nb_multiply*/
	(binaryfunc)Wrapper_div,	/*nb_divide*/
	(binaryfunc)Wrapper_mod,	/*nb_remainder*/
	(binaryfunc)Wrapper_divmod,	/*nb_divmod*/
	(ternaryfunc)Wrapper_pow,	/*nb_power*/
	(unaryfunc)Wrapper_neg,		/*nb_negative*/
	(unaryfunc)Wrapper_pos,		/*nb_positive*/
	(unaryfunc)Wrapper_abs,		/*nb_absolute*/
	(inquiry)Wrapper_nonzero,	/*nb_nonzero*/
	(unaryfunc)Wrapper_invert,	/*nb_invert*/
	(binaryfunc)Wrapper_lshift,	/*nb_lshift*/
	(binaryfunc)Wrapper_rshift,	/*nb_rshift*/
	(binaryfunc)Wrapper_and,	/*nb_and*/
	(binaryfunc)Wrapper_xor,	/*nb_xor*/
	(binaryfunc)Wrapper_or,		/*nb_or*/
	(coercion)Wrapper_coerce,	/*nb_coerce*/
	(unaryfunc)Wrapper_int,		/*nb_int*/
	(unaryfunc)Wrapper_long,	/*nb_long*/
	(unaryfunc)Wrapper_float,	/*nb_float*/
	(unaryfunc)Wrapper_oct,		/*nb_oct*/
	(unaryfunc)Wrapper_hex,		/*nb_hex*/
};


/* -------------------------------------------------------- */


static char *acquire_args[] = {"object", "name", "filter", "extra", "explicit",
			       "default", "containment", NULL};

static PyObject *
Wrapper_acquire_method(Wrapper *self, PyObject *args, PyObject *kw)
{
  PyObject *name, *filter=0, *extra=Py_None;
  PyObject *expl=0, *defalt=0;
  int explicit=1;
  int containment=0;

  UNLESS (PyArg_ParseTupleAndKeywords(
	     args, kw, "O|OOOOi", acquire_args+1,
	     &name, &filter, &extra, &explicit, &defalt, &containment
	     ))
    return NULL;

  if (expl) explicit=PyObject_IsTrue(expl);

  if (filter==Py_None) filter=0;

  return Wrapper_findattr(self,name,filter,extra,OBJECT(self),1,
			  explicit || 
			  self->ob_type==(PyTypeObject*)&Wrappertype,
			  explicit, containment);
}

static PyObject *
Wrapper_inContextOf(Wrapper *self, PyObject *args)
{
  PyObject *o, *c;
  int inner=1;

  UNLESS(PyArg_ParseTuple(args,"O|i",&o,&inner)) return NULL;

  if (inner) {
    /* o = aq_base(o) */
    while (isWrapper(o) && WRAPPER(o)->obj) o=WRAPPER(o)->obj;

    /* while 1: */
    while (1) {

      /*   if aq_base(self) is o: return 1 */
      c = self->obj;
      while (isWrapper(c) && WRAPPER(c)->obj) c = WRAPPER(c)->obj;
      if (c == o) return PyInt_FromLong(1);

      /*   self = aq_parent(aq_inner(self)) */
      /*   if self is None: break */
      while (self->obj && isWrapper(self->obj)) self = WRAPPER(self->obj);
      if (self->container && isWrapper(self->container))
        self = WRAPPER(self->container);
      else break;
    }
  }
  else {
    /* Follow wrappers instead. */
    c = OBJECT(self);
    while (1) {
      if (c==o) return PyInt_FromLong(1);
      if (c && isWrapper(c)) c=WRAPPER(c)->container;
      else break;
    }
  }

  return PyInt_FromLong(0);
}

static struct PyMethodDef Wrapper_methods[] = {
  {"__init__", (PyCFunction)Wrapper__init__, 0,
   "Initialize an Acquirer Wrapper"},
  {"acquire", (PyCFunction)Wrapper_acquire_method, 
   METH_VARARGS|METH_KEYWORDS,
   "Get an attribute, acquiring it if necessary"},
  {"aq_acquire", (PyCFunction)Wrapper_acquire_method, 
   METH_VARARGS|METH_KEYWORDS,
   "Get an attribute, acquiring it if necessary"},
  {"aq_inContextOf", (PyCFunction)Wrapper_inContextOf, METH_VARARGS,
   "Test whether the object is currently in the context of the argument"},
  {NULL,		NULL}		/* sentinel */
};

static PyExtensionClass Wrappertype = {
  PyObject_HEAD_INIT(NULL)
  0,					/*ob_size*/
  "ImplicitAcquirerWrapper",		/*tp_name*/
  sizeof(Wrapper),       		/*tp_basicsize*/
  0,					/*tp_itemsize*/
  /* methods */
  (destructor)Wrapper_dealloc,		/*tp_dealloc*/
  (printfunc)0,				/*tp_print*/
  (getattrfunc)0,			/*tp_getattr*/
  (setattrfunc)0,			/*tp_setattr*/
  (cmpfunc)Wrapper_compare,    		/*tp_compare*/
  (reprfunc)Wrapper_repr,      		/*tp_repr*/
  &Wrapper_as_number,			/*tp_as_number*/
  &Wrapper_as_sequence,			/*tp_as_sequence*/
  &Wrapper_as_mapping,			/*tp_as_mapping*/
  (hashfunc)Wrapper_hash,      		/*tp_hash*/
  (ternaryfunc)Wrapper_call,		/*tp_call*/
  (reprfunc)Wrapper_str,       		/*tp_str*/
  (getattrofunc)Wrapper_getattro,	/*tp_getattr with object key*/
  (setattrofunc)Wrapper_setattro,      	/*tp_setattr with object key*/

  /* Space for future expansion */
  0L,0L,
  "Wrapper object for implicit acquisition", /* Documentation string */
  METHOD_CHAIN(Wrapper_methods),
  EXTENSIONCLASS_BINDABLE_FLAG,
};

static PyExtensionClass XaqWrappertype = {
  PyObject_HEAD_INIT(NULL)
  0,					/*ob_size*/
  "ExplicitAcquirerWrapper",		/*tp_name*/
  sizeof(Wrapper),       		/*tp_basicsize*/
  0,					/*tp_itemsize*/
  /* methods */
  (destructor)Wrapper_dealloc,		/*tp_dealloc*/
  (printfunc)0,				/*tp_print*/
  (getattrfunc)0,			/*tp_getattr*/
  (setattrfunc)0,			/*tp_setattr*/
  (cmpfunc)Wrapper_compare,    		/*tp_compare*/
  (reprfunc)Wrapper_repr,      		/*tp_repr*/
  &Wrapper_as_number,			/*tp_as_number*/
  &Wrapper_as_sequence,			/*tp_as_sequence*/
  &Wrapper_as_mapping,			/*tp_as_mapping*/
  (hashfunc)Wrapper_hash,      		/*tp_hash*/
  (ternaryfunc)Wrapper_call,		/*tp_call*/
  (reprfunc)Wrapper_str,       		/*tp_str*/
  (getattrofunc)Xaq_getattro,		/*tp_getattr with object key*/
  (setattrofunc)Wrapper_setattro,      	/*tp_setattr with object key*/

  /* Space for future expansion */
  0L,0L,
  "Wrapper object for explicit acquisition", /* Documentation string */
  METHOD_CHAIN(Wrapper_methods),
  EXTENSIONCLASS_BINDABLE_FLAG,
};

static PyObject *
acquire_of(PyObject *self, PyObject *args)
{
  PyObject *inst;

  UNLESS(PyArg_ParseTuple(args, "O", &inst)) return NULL;

  UNLESS(PyExtensionInstance_Check(inst))
    {
      PyErr_SetString(PyExc_TypeError,
		      "attempt to wrap extension method using an object that\n"
		      "is not an extension class instance.");
      return NULL;
    }

  return newWrapper(self, inst, (PyTypeObject *)&Wrappertype);
}

static PyObject *
xaq_of(PyObject *self, PyObject *args)
{
  PyObject *inst;

  UNLESS(PyArg_ParseTuple(args, "O", &inst)) return NULL;

  UNLESS(PyExtensionInstance_Check(inst))
    {
      PyErr_SetString(PyExc_TypeError,
		      "attempt to wrap extension method using an object that\n"
		      "is not an extension class instance.");
      return NULL;
    }

  return newWrapper(self, inst, (PyTypeObject *)&XaqWrappertype);
}

static struct PyMethodDef Acquirer_methods[] = {
  {"__of__",(PyCFunction)acquire_of, METH_VARARGS, 
   "__of__(context) -- return the object in a context"},
  
  {NULL,		NULL}		/* sentinel */
};

static struct PyMethodDef Xaq_methods[] = {
  {"__of__",(PyCFunction)xaq_of, METH_VARARGS,""},
  
  {NULL,		NULL}		/* sentinel */
};

static PyObject *
capi_aq_acquire(PyObject *self, PyObject *name, PyObject *filter,
	PyObject *extra, int explicit, PyObject *defalt, int containment)
{
  
  PyObject *result;

  if (filter==Py_None) filter=0;

  /* We got a wrapped object, so business as usual */
  if (isWrapper(self)) 
    return Wrapper_findattr(
	      WRAPPER(self), name, filter, extra, OBJECT(self),1,
	      explicit || 
	      WRAPPER(self)->ob_type==(PyTypeObject*)&Wrappertype,
	      explicit, containment);
  
  /* Not wrapped and no filter, so just getattr */
  if (! filter) return PyObject_GetAttr(self, name);

  /* Crap, we've got to construct a wrapper so we can use Wrapper_findattr */
  UNLESS (self=newWrapper(self, NULL, (PyTypeObject*)&Wrappertype)) 
    return NULL;
  
  result=Wrapper_findattr(WRAPPER(self), name, filter, extra, OBJECT(self),
			   1, 1, explicit, containment);

  /* get rid of temp wrapper */
  Py_DECREF(self);

  return result;
}

static PyObject *
module_aq_acquire(PyObject *ignored, PyObject *args, PyObject *kw)
{
  PyObject *self;
  PyObject *name, *filter=0, *extra=Py_None;
  PyObject *expl=0, *defalt=0;
  int explicit=1, containment=0;

  UNLESS (PyArg_ParseTupleAndKeywords(
	     args, kw, "OO|OOOOi", acquire_args,
	     &self, &name, &filter, &extra, &expl, &defalt, &containment
	     ))
    return NULL;

  if (expl) explicit=PyObject_IsTrue(expl);

  return capi_aq_acquire(self, name, filter, extra, explicit, defalt,
  	containment);
}

static PyObject *
capi_aq_get(PyObject *self, PyObject *name, PyObject *defalt, int containment)
{
  PyObject *result = NULL;
  /* We got a wrapped object, so business as usual */
  if (isWrapper(self)) 
    result=Wrapper_findattr(WRAPPER(self), name, 0, 0, OBJECT(self), 1, 1, 1, 
		       containment);
  else
    result=PyObject_GetAttr(self, name);

  if (! result && defalt)
    {
      PyErr_Clear();
      result=defalt;
      Py_INCREF(result);
    }
  
  return result;
}


static PyObject *
module_aq_get(PyObject *r, PyObject *args)
{
  PyObject *self, *name, *defalt=0;
  int containment=0;
  
  UNLESS (PyArg_ParseTuple(args, "OO|Oi", 
			   &self, &name, &defalt, &containment
			   )) return NULL;
  return capi_aq_get(self, name, defalt, containment);
}

static int 
capi_aq_iswrapper(PyObject *self) {
	return isWrapper(self);
}

static PyObject *
capi_aq_base(PyObject *self)
{
  PyObject *result;
  if (! isWrapper(self)) 
    {
      Py_INCREF(self);
      return self;
    }
  
  if (WRAPPER(self)->obj)
    {
      result=WRAPPER(self)->obj;
      while (isWrapper(result) && WRAPPER(result)->obj)
      	result=WRAPPER(result)->obj;
    }
  else result=Py_None;
  Py_INCREF(result);
  return result;
}

static PyObject *
module_aq_base(PyObject *ignored, PyObject *args)
{
  PyObject *self;
  UNLESS (PyArg_ParseTuple(args, "O", &self)) return NULL;

  return capi_aq_base(self);
}

static PyObject *
capi_aq_parent(PyObject *self)
{
  PyObject *result=Py_None;

  if (isWrapper(self) && WRAPPER(self)->container)
  	result=WRAPPER(self)->container;

  Py_INCREF(result);
  return result;
}

static PyObject *
module_aq_parent(PyObject *ignored, PyObject *args)
{
  PyObject *self;

  UNLESS (PyArg_ParseTuple(args, "O", &self)) return NULL;

  return capi_aq_parent(self);
}

static PyObject *
capi_aq_self(PyObject *self)
{
  PyObject *result;
  if (! isWrapper(self)) 
    {
      Py_INCREF(self);
      return self;
    }
  
  if (WRAPPER(self)->obj) result=WRAPPER(self)->obj;
  else result=Py_None;

  Py_INCREF(result);
  return result;
}

static PyObject *
module_aq_self(PyObject *ignored, PyObject *args)
{
  PyObject *self;
  UNLESS (PyArg_ParseTuple(args, "O", &self)) return NULL;
  return capi_aq_self(self);
}

static PyObject *
capi_aq_inner(PyObject *self)
{
  PyObject *result;
  if (! isWrapper(self)) 
    {
      Py_INCREF(self);
      return self;
    }

  if (WRAPPER(self)->obj)
    {
      result=WRAPPER(self)->obj;
      while (isWrapper(result) && WRAPPER(result)->obj) 
	{
	  self=result;
	  result=WRAPPER(result)->obj;
	}
      result=self;
    }
  else result=Py_None;

  Py_INCREF(result);
  return result;
}

static PyObject *
module_aq_inner(PyObject *ignored, PyObject *args)
{
  PyObject *self;

  UNLESS (PyArg_ParseTuple(args, "O", &self)) return NULL;
  return capi_aq_inner(self);
}

static PyObject *
capi_aq_chain(PyObject *self, int containment)
{
  PyObject *result;

  UNLESS (result=PyList_New(0)) return NULL;

  while (1)
    {
      if (isWrapper(self))
	{
	  if (WRAPPER(self)->obj)
	    {
	      if (containment)
		while (WRAPPER(self)->obj && isWrapper(WRAPPER(self)->obj))
		  self=WRAPPER(self)->obj;
	      if (PyList_Append(result,OBJECT(self)) < 0)
		goto err;
	    }
	  if (WRAPPER(self)->container) 
	    {
	      self=WRAPPER(self)->container;
	      continue;
	    }
	}
      else
	if (PyList_Append(result, self) < 0)
	  goto err;

      break;
    }
  
  return result;
err:
  Py_DECREF(result);
  return result;
}

static PyObject *
module_aq_chain(PyObject *ignored, PyObject *args)
{
  PyObject *self;
  int containment=0;

  UNLESS (PyArg_ParseTuple(args, "O|i", &self, &containment))
    return NULL;

  return capi_aq_chain(self, containment);
}

static struct PyMethodDef methods[] = {
  {"aq_acquire", (PyCFunction)module_aq_acquire, METH_VARARGS|METH_KEYWORDS, 
   "aq_acquire(ob, name [, filter, extra, explicit]) -- "
   "Get an attribute, acquiring it if necessary"
  },
  {"aq_get", (PyCFunction)module_aq_get, METH_VARARGS,
   "aq_get(ob, name [, default]) -- "
   "Get an attribute, acquiring it if necessary."
  },
  {"aq_base", (PyCFunction)module_aq_base, METH_VARARGS, 
   "aq_base(ob) -- Get the object unwrapped"},
  {"aq_parent", (PyCFunction)module_aq_parent, METH_VARARGS, 
   "aq_parent(ob) -- Get the parent of an object"},
  {"aq_self", (PyCFunction)module_aq_self, METH_VARARGS, 
   "aq_self(ob) -- Get the object with the outermost wrapper removed"},
  {"aq_inner", (PyCFunction)module_aq_inner, METH_VARARGS, 
   "aq_inner(ob) -- "
   "Get the object with alll but the innermost wrapper removed"},
  {"aq_chain", (PyCFunction)module_aq_chain, METH_VARARGS, 
   "aq_chain(ob [, containment]) -- "
   "Get a list of objects in the acquisition environment"},
  {NULL,	NULL}
};

void
initAcquisition(void)
{
  PyObject *m, *d;
  PyObject *api;
  char *rev="$Revision: 1.52 $";
  PURE_MIXIN_CLASS(Acquirer,
    "Base class for objects that implicitly"
    " acquire attributes from containers\n"
    , Acquirer_methods);
  PURE_MIXIN_CLASS(ExplicitAcquirer,
    "Base class for objects that explicitly"
    " acquire attributes from containers\n"
    , Xaq_methods);

  UNLESS(ExtensionClassImported) return;

  UNLESS(Acquired=PyString_FromStringAndSize(NULL,42)) return;
  strcpy(PyString_AsString(Acquired),
	 "<Special Object Used to Force Acquisition>");

  /* Create the module and add the functions */
  m = Py_InitModule4("Acquisition", methods,
	   "Provide base classes for acquiring objects\n\n"
	   "$Id: Acquisition.c,v 1.52 2001/07/03 19:38:20 matt Exp $\n",
		     OBJECT(NULL),PYTHON_API_VERSION);

  d = PyModule_GetDict(m);
  init_py_names();
  PyExtensionClass_Export(d,"Acquirer",AcquirerType);
  PyExtensionClass_Export(d,"ImplicitAcquisitionWrapper",Wrappertype);
  PyExtensionClass_Export(d,"ExplicitAcquirer",ExplicitAcquirerType);
  PyExtensionClass_Export(d,"ExplicitAcquisitionWrapper",XaqWrappertype);

  /* Create aliases */
  PyDict_SetItemString(d,"Implicit",OBJECT(&AcquirerType));
  PyDict_SetItemString(d,"Explicit",OBJECT(&ExplicitAcquirerType));
  
  PyDict_SetItemString(d,"__version__",
		       PyString_FromStringAndSize(rev+11,strlen(rev+11)-2));
  PyDict_SetItemString(d,"Acquired",Acquired);

  AcquisitionCAPI.AQ_Acquire = capi_aq_acquire;
  AcquisitionCAPI.AQ_Get = capi_aq_get;
  AcquisitionCAPI.AQ_IsWrapper = capi_aq_iswrapper;
  AcquisitionCAPI.AQ_Base = capi_aq_base;
  AcquisitionCAPI.AQ_Parent = capi_aq_parent;
  AcquisitionCAPI.AQ_Self = capi_aq_self;
  AcquisitionCAPI.AQ_Inner = capi_aq_inner;
  AcquisitionCAPI.AQ_Chain = capi_aq_chain;

  api = PyCObject_FromVoidPtr(&AcquisitionCAPI, NULL);
  PyDict_SetItemString(d, "AcquisitionCAPI", api);
  Py_DECREF(api);

  CHECK_FOR_ERRORS("can't initialize module Acquisition");
}

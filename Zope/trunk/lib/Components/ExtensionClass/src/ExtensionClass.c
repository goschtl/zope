/*

  $Id: ExtensionClass.c,v 1.5 1997/02/17 16:27:53 jim Exp $

  Extension Class


     Copyright 

       Copyright 1996 Digital Creations, L.C., 910 Princess Anne
       Street, Suite 300, Fredericksburg, Virginia 22401 U.S.A. All
       rights reserved.  Copyright in this software is owned by DCLC,
       unless otherwise indicated. Permission to use, copy and
       distribute this software is hereby granted, provided that the
       above copyright notice appear in all copies and that both that
       copyright notice and this permission notice appear. Note that
       any product, process or technology described in this software
       may be the subject of other Intellectual Property rights
       reserved by Digital Creations, L.C. and are not licensed
       hereunder.

     Trademarks 

       Digital Creations & DCLC, are trademarks of Digital Creations, L.C..
       All other trademarks are owned by their respective companies. 

     No Warranty 

       The software is provided "as is" without warranty of any kind,
       either express or implied, including, but not limited to, the
       implied warranties of merchantability, fitness for a particular
       purpose, or non-infringement. This software could include
       technical inaccuracies or typographical errors. Changes are
       periodically made to the software; these changes will be
       incorporated in new editions of the software. DCLC may make
       improvements and/or changes in this software at any time
       without notice.

     Limitation Of Liability 

       In no event will DCLC be liable for direct, indirect, special,
       incidental, economic, cover, or consequential damages arising
       out of the use of or inability to use this software even if
       advised of the possibility of such damages. Some states do not
       allow the exclusion or limitation of implied warranties or
       limitation of liability for incidental or consequential
       damages, so the above limitation or exclusion may not apply to
       you.

    If you have questions regarding this software,
    contact:
   
      Jim Fulton, jim@digicool.com
      Digital Creations L.C.  
   
      (540) 371-6909

  $Log: ExtensionClass.c,v $
  Revision 1.5  1997/02/17 16:27:53  jim
  Many changes.

  Revision 1.4  1996/12/06 17:12:29  jim
  Major speed enhancements for attribute lookup and calling special
  methods.

  Revision 1.3  1996/10/24 21:07:49  jim
  Fixed bug in returning __bases__ for base classes.
  Added missing PyErr_Clear() call.

  Revision 1.2  1996/10/23 18:36:56  jim
  Changed a bunch of single quotes to double and got rid of
  some superfluous semicolns that caused warning on SGI.

  Fixed bug in CCL_getattr when getting the __base__ attribute of a base
  class.

  Fixed a doc string.

  Revision 1.1  1996/10/22 22:26:08  jim
  *** empty log message ***


*/

static char ExtensionClass_module_documentation[] = 
"ExtensionClass - Classes implemented in c\n"
"\n"
"Built-in C classes are like Built-in types except that\n"
"they provide some of the behavior of Python classes:\n"
"\n"
"  - They provide access to unbound methods,\n"
"  - They can be called to create instances.\n"
"\n"
"$Id: ExtensionClass.c,v 1.5 1997/02/17 16:27:53 jim Exp $\n"
;

#include <stdio.h>
#include "Python.h"
#include "PyErr_Format.c"

static void
PyVar_Assign(PyObject **v,  PyObject *e)
{
  Py_XDECREF(*v);
  *v=e;
}

#define ASSIGN(V,E) PyVar_Assign(&(V),(E))
#define UNLESS(E) if(!(E))
#define UNLESS_ASSIGN(V,E) ASSIGN(V,E); UNLESS(V)

#define INSTANCE_DICT(inst) \
*(((PyObject**)inst) + (inst->ob_type->tp_basicsize/sizeof(PyObject*) - 1))


/* Declarations for objects of type ExtensionClass */
#include "ExtensionClass.h"

staticforward PyExtensionClass ECType;

#define ExtensionClass_Check(O) ((O)->ob_type == (PyTypeObject*)&ECType)
#define ExtensionInstance_Check(O) \
   ((O)->ob_type->ob_type == (PyTypeObject*)&ECType)
#define AsExtensionClass(O) ((PyExtensionClass*)(O))
#define ExtensionClassOf(O) ((PyExtensionClass*)((O)->ob_type))
#define AsPyObject(O) ((PyObject*)(O))
#define NeedsToBeBound(O) \
   ((O)->ob_type->ob_type == (PyTypeObject*)&ECType && \
    (((PyExtensionClass*)((O)->ob_type))->class_flags & \
     EXTENSIONCLASS_BINDABLE_FLAG))

static PyObject *py__add__, *py__sub__, *py__mul__, *py__div__,
  *py__mod__, *py__pow__, *py__divmod__, *py__lshift__, *py__rshift__,
  *py__and__, *py__or__, *py__xor__, *py__coerce__, *py__neg__,
  *py__pos__, *py__abs__, *py__nonzero__, *py__inv__, *py__int__,
  *py__long__, *py__float__, *py__oct__, *py__hex__,
  *py__getitem__, *py__setitem__, *py__delitem__,
  *py__getslice__, *py__setslice__, *py__delslice__,
  *py__concat__, *py__repeat__, *py__len__, *py__of__, *py__call__,
  *py__getattr__, *py__setattr__, *py__delattr__,
  *py__del__, *py__repr__, *py__str__, *py__class__,
  *py__hash__, *py__cmp__, *py__var_size__, *py__init__, *py__getinitargs__,
  *py__getstate__, *py__setstate__, *py__dict__, *pyclass_;

static void
init_py_names()
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
  INIT_PY_NAME(__inv__);
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
  INIT_PY_NAME(__concat__);
  INIT_PY_NAME(__repeat__);
  INIT_PY_NAME(__len__);
  INIT_PY_NAME(__of__);
  INIT_PY_NAME(__call__);
  INIT_PY_NAME(__getattr__);
  INIT_PY_NAME(__setattr__);
  INIT_PY_NAME(__delattr__);
  INIT_PY_NAME(__del__);
  INIT_PY_NAME(__repr__);
  INIT_PY_NAME(__str__);
  INIT_PY_NAME(__class__);
  INIT_PY_NAME(__hash__);
  INIT_PY_NAME(__cmp__);
  INIT_PY_NAME(__var_size__);
  INIT_PY_NAME(__init__);
  INIT_PY_NAME(__getinitargs__);
  INIT_PY_NAME(__getstate__);
  INIT_PY_NAME(__setstate__);
  INIT_PY_NAME(__dict__);
  INIT_PY_NAME(class_);
  
#undef INIT_PY_NAME
}

static PyObject *
CallMethodO(PyObject *self, PyObject *name,
		     PyObject *args, PyObject *kw)
{
  if(! args && PyErr_Occurred()) return NULL;
  UNLESS(name=PyObject_GetAttr(self,name)) return NULL;
  ASSIGN(name,PyEval_CallObjectWithKeywords(name,args,kw));
  if(args) Py_DECREF(args);
  return name;
}

#define Build Py_BuildValue

/* CMethod objects: */

typedef struct {
  PyObject_HEAD
  PyTypeObject *type;
  PyObject *self;
  char		*name;
  PyCFunction	meth;
  int		flags;
  char		*doc;
} CMethod;

staticforward PyTypeObject CMethodType;

#define CMethod_Check(O) ((O)->ob_type==&CMethodType)
#define UnboundCMethod_Check(O) \
  ((O)->ob_type==&CMethodType && ! ((CMethod*)(O))->self)
#define AsCMethod(O) ((CMethod*)(O))

static int
CMethod_issubclass(PyExtensionClass *sub, PyExtensionClass *type)
{
  int i,l;
  PyObject *t;

  if(sub==type) return 1;
  if(! sub->bases) return 0;
  l=PyTuple_Size(sub->bases);
  for(i=0; i < l; i++)
    {
      t=PyTuple_GET_ITEM(sub->bases, i);
      if(t==(PyObject*)type) return 1;
      if(ExtensionClass_Check(t)
	 && AsExtensionClass(t)->bases
	 && CMethod_issubclass(AsExtensionClass(t),type)
	 ) return 1;
    }
  return 0;
}

#define Subclass_Check(C1,C2) \
  CMethod_issubclass((PyExtensionClass *)(C1), (PyExtensionClass *)(C2))

#define SubclassInstance_Check(C1,C2) \
  CMethod_issubclass((PyExtensionClass *)((C1)->ob_type), \
		     (PyExtensionClass *)(C2))


static PyObject *
newCMethod(PyExtensionClass *type, PyObject *inst,
	   char *name, PyCFunction meth, int flags, char *doc)
{
  CMethod *self;

  
  UNLESS(self = PyObject_NEW(CMethod, &CMethodType)) return NULL;
  Py_INCREF(type);
  Py_XINCREF(inst);
  self->type=(PyTypeObject*)type;
  self->self=inst;
  self->name=name;
  self->meth=meth;
  self->flags=flags;
  self->doc=doc;
  return (PyObject*)self;
}

static CMethod *
bindCMethod(CMethod *m, PyObject *inst)
{
  CMethod *self;
  
  UNLESS(inst->ob_type==m->type ||
	 (ExtensionInstance_Check(inst)
	  && SubclassInstance_Check(inst,m->type))
	 )
    {
      Py_INCREF(m);
      return m;
    }

  UNLESS(self = PyObject_NEW(CMethod, &CMethodType)) return NULL;

  Py_INCREF(inst);
  Py_INCREF(m->type);
  self->type=m->type;
  self->self=inst;
  self->name=m->name;
  self->meth=m->meth;
  self->flags=m->flags;
  self->doc=m->doc;
  return self;
}

static void
CMethod_dealloc(CMethod *self)
{
#ifdef TRACE_DEALLOC
  fprintf(stderr,"Deallocating C method %s\n", self->name); 
#endif
  Py_XDECREF(self->type);
  Py_XDECREF(self->self);
  PyMem_DEL(self);
}

static PyObject *
call_cmethod(CMethod *self, PyObject *inst, PyObject *args, PyObject *kw)
{
  if (!(self->flags & METH_VARARGS)) {
    int size = PyTuple_Size(args);
    if (size == 1)
      args = PyTuple_GET_ITEM(args, 0);
    else if (size == 0)
      args = NULL;
  }
  if (self->flags & METH_KEYWORDS)
    return (*(PyCFunctionWithKeywords)self->meth)(inst, args, kw);
  else
    {
      if (kw != NULL && PyDict_Size(kw) != 0)
	{
	  PyErr_SetString(PyExc_TypeError,
			  "this function takes no keyword arguments");
	  return NULL;
	}
      return (*self->meth)(inst, args);
    }
}

static PyObject *
CMethod_call(CMethod *self, PyObject *args, PyObject *kw)
{
  int size;

  if(self->self) return call_cmethod(self,self->self,args,kw);

  if((size=PyTuple_Size(args)) > 0)
    {
      PyObject *first=0;
      UNLESS(first=PyTuple_GET_ITEM(args, 0)) return NULL;
      if(first->ob_type==self->type
	 ||
	 (ExtensionInstance_Check(first)
	  &&
	  CMethod_issubclass(ExtensionClassOf(first),
			     AsExtensionClass(self->type))
	  )
	 );
      {
	PyObject *rest=0;
	UNLESS(rest=PySequence_GetSlice(args,1,size)) return NULL;
	ASSIGN(rest,call_cmethod(self,first,rest,kw));
	return rest;
      }
    }

  return PyErr_Format(PyExc_TypeError,
		      "unbound C method must be called with %s 1st argument",
		      "s", self->type->tp_name);
}

static PyObject *
CMethod_getattr(CMethod *self, char *name)
{
  PyObject *r;

  if(strcmp(name,"__name__")==0 || strcmp(name,"func_name")==0 )
    return PyString_FromString(self->name);
  if(strcmp(name,"func_code")==0 ||
     strcmp(name,"im_func")==0)
    {
      Py_INCREF(self);
      return (PyObject *)self;
    }
  if(strcmp(name,"__doc__")==0 ||
     strcmp(name,"func_doc")==0 ||
     strcmp(name,"func_doc")==0)
    {
      if(self->doc)
	return PyString_FromString(self->doc);
      else
	return PyString_FromString("");
    }
  if(strcmp(name,"im_class")==0)
    {
      Py_INCREF(self->type);
      return (PyObject *)self->type;
    }
  if(strcmp(name,"im_self")==0)
    {
      if(self->self) r=self->self;
      else           r=Py_None;
      Py_INCREF(r);
      return r;
    }
  PyErr_SetString(PyExc_AttributeError, name);
  return NULL;
}

static PyTypeObject CMethodType = {
  PyObject_HEAD_INIT(NULL)
  0,				/*ob_size*/
  "CMethod",			/*tp_name*/
  sizeof(CMethod),		/*tp_basicsize*/
  0,				/*tp_itemsize*/
  /* methods */
  (destructor)CMethod_dealloc,	/*tp_dealloc*/
  (printfunc)0,			/*tp_print*/
  (getattrfunc)CMethod_getattr,	/*tp_getattr*/
  (setattrfunc)0,		/*tp_setattr*/
  (cmpfunc)0,			/*tp_compare*/
  (reprfunc)0,			/*tp_repr*/
  0,				/*tp_as_number*/
  0,				/*tp_as_sequence*/
  0,				/*tp_as_mapping*/
  (hashfunc)0,			/*tp_hash*/
  (ternaryfunc)CMethod_call,	/*tp_call*/
  (reprfunc)0,			/*tp_str*/
  
  /* Space for future expansion */
  0L,0L,0L,0L,
  "Storage manager for unbound C function PyObject data"
  /* Documentation string */
};

/* PMethod objects: */

#define PMethod PyECMethodObject

staticforward PyTypeObject PMethodType;

#define PMethod_Check(O) ((O)->ob_type==&PMethodType)
#define UnboundPMethod_Check(O) \
  ((O)->ob_type==&PMethodType && ! ((PMethod*)(O))->self)

#define UnboundEMethod_Check(O) \
  (((O)->ob_type==&PMethodType ||(O)->ob_type==&CMethodType) \
   && ! ((PMethod*)(O))->self)


static PyObject *
newPMethod(PyExtensionClass *type, PyObject *meth)
{
  PMethod *self;
  
  UNLESS(self = PyObject_NEW(PMethod, &PMethodType)) return NULL;
  Py_INCREF(type);
  Py_INCREF(meth);
  self->type=(PyTypeObject*)type;
  self->self=NULL;
  self->meth=meth;
  return (PyObject*)self;
}

static PyObject *
bindPMethod(PMethod *m, PyObject *inst)
{
  PMethod *self;

  if(NeedsToBeBound(m->meth))
    return CallMethodO(m->meth, py__of__, Build("(O)", inst), NULL);
  if(m->ob_refcnt==1)
    {
      Py_INCREF(inst);
      ASSIGN(m->self, inst);
      Py_INCREF(m);
      return (PyObject*)m;
    }
  
  UNLESS(self = PyObject_NEW(PMethod, &PMethodType)) return NULL;

  Py_INCREF(inst);
  Py_INCREF(m->type);
  self->type=m->type;
  self->self=inst;
  self->meth=m->meth;
  return (PyObject*)self;
}

static PyObject *
PMethod_New(PyObject *meth, PyObject *inst)
{
  if(PMethod_Check(meth)) return bindPMethod((PMethod*)meth,inst);
  UNLESS(ExtensionInstance_Check(inst))
    return PyErr_Format(PyExc_TypeError,
			"Attempt to use %s as method for %s, which is "
			"not an extension class instance.",
			"OO",meth,inst);
  if(meth=newPMethod(ExtensionClassOf(inst), meth))
    UNLESS_ASSIGN(((PMethod*)meth)->self,inst) return NULL;
  Py_INCREF(inst);
  return meth;
}

static void
PMethod_dealloc(PMethod *self)
{
#ifdef TRACE_DEALLOC
  fprintf(stderr,"Deallocating PM ... ");
#endif
  Py_XDECREF(self->type);
  Py_XDECREF(self->self);
  PyMem_DEL(self);
#ifdef TRACE_DEALLOC
  fprintf(stderr," Done Deallocating PM\n");
#endif
}  

static PyObject *
call_PMethod(PMethod *self, PyObject *inst, PyObject *args, PyObject *kw)
{
  PyObject *a;

  a=Py_BuildValue("(O)",inst);
  if(a) ASSIGN(a,PySequence_Concat(a,args));
  if(a) ASSIGN(a,PyEval_CallObjectWithKeywords(self->meth,a,kw));
  return a;
}

static PyObject *
PMethod_call(PMethod *self, PyObject *args, PyObject *kw)
{
  int size;

  if(self->self) return call_PMethod(self,self->self,args,kw);

  if((size=PyTuple_Size(args)) > 0)
    {
      PyObject *first=0, *ftype=0;
      UNLESS(first=PyTuple_GET_ITEM(args, 0)) return NULL;
      if(! self->type ||
	 ((ftype=PyObject_GetAttr(first,py__class__)) &&
	  (ftype==(PyObject*)self->type ||
	   (ExtensionClass_Check(ftype) &&
	    CMethod_issubclass(AsExtensionClass(ftype),
			       AsExtensionClass(self->type))
	    )
	   )
	  )
	 )
	{
	  if(NeedsToBeBound(self->meth))
	    {
	      PyObject *r, *rest;
	      UNLESS(r=CallMethodO(self->meth,py__of__,Build("(O)", first),
				   NULL))
		return NULL;
	      UNLESS(rest=PySequence_GetSlice(args,1,size))
		{
		  Py_DECREF(r);
		  return NULL;
		}
	      ASSIGN(r,PyEval_CallObjectWithKeywords(r,rest,kw));
	      Py_DECREF(rest);
	      return r;
	    }
	  Py_DECREF(ftype);
	  return PyEval_CallObjectWithKeywords(self->meth,args,kw);
	}
      Py_XDECREF(ftype);
    }

  return PyErr_Format(PyExc_TypeError,
		      "unbound Python method must be called with %s"
		      " 1st argument",
		      "s", self->type->tp_name);
}

static PyObject *
PMethod_getattr(PMethod *self, char *name)
{
  PyObject *r;

  if(strcmp(name,"__name__")==0 || strcmp(name,"func_name")==0 )
    return PyObject_GetAttrString(self->meth,"__name__");
  if(strcmp(name,"im_func")==0)
    {
      Py_INCREF(self->meth);
      return self->meth;
    }
  if(strcmp(name,"__doc__")==0 ||
     strcmp(name,"func_doc")==0 ||
     strcmp(name,"func_doc")==0)
    return PyObject_GetAttrString(self->meth,"__doc__");
  if(strcmp(name,"im_class")==0)
    {
      Py_INCREF(self->type);
      return (PyObject *)self->type;
    }
  if(strcmp(name,"im_self")==0)
    {
      if(self->self) r=self->self;
      else           r=Py_None;
      Py_INCREF(r);
      return r;
    }
  PyErr_SetString(PyExc_AttributeError, name);
  return NULL;
}

static PyTypeObject PMethodType = {
  PyObject_HEAD_INIT(NULL)
  0,				/*ob_size*/
  "Python Method",		/*tp_name*/
  sizeof(PMethod),		/*tp_basicsize*/
  0,				/*tp_itemsize*/
  /* methods */
  (destructor)PMethod_dealloc,	/*tp_dealloc*/
  (printfunc)0,			/*tp_print*/
  (getattrfunc)PMethod_getattr,	/*tp_getattr*/
  (setattrfunc)0,		/*tp_setattr*/
  (cmpfunc)0,			/*tp_compare*/
  (reprfunc)0,			/*tp_repr*/
  0,				/*tp_as_number*/
  0,				/*tp_as_sequence*/
  0,				/*tp_as_mapping*/
  (hashfunc)0,			/*tp_hash*/
  (ternaryfunc)PMethod_call,	/*tp_call*/
  (reprfunc)0,			/*tp_str*/
  
  /* Space for future expansion */
  0L,0L,0L,0L,
  "Storage manager for unbound C function PyObject data"
  /* Documentation string */
};

static PyObject *CCL_getattr(PyExtensionClass*,PyObject*,int);

/* Special Methods */

#define UNARY_OP(OP) \
static PyObject * \
OP ## _by_name(PyObject *self, PyObject *args) { \
  UNLESS(PyArg_Parse(args,"")) return NULL; \
  return self->ob_type->tp_ ## OP(self); \
} 

UNARY_OP(repr)
UNARY_OP(str)

static PyObject * 
hash_by_name(PyObject *self, PyObject *args) { 
  long r; 
  UNLESS(PyArg_Parse(args,"")) return NULL; 
  UNLESS(-1 != (r=self->ob_type->tp_hash(self))) return NULL; 
  return PyInt_FromLong(r); 
} 

static PyObject *
call_by_name(PyObject *self, PyObject *args, PyObject *kw)
{
  return self->ob_type->tp_call(self,args,kw);
}

static PyObject *
compare_by_name(PyObject *self, PyObject *args)
{
  PyObject *other;

  UNLESS(PyArg_Parse(args,"O", &other)) return NULL; 
  return PyInt_FromLong(self->ob_type->tp_compare(self,other)); 
} 

static PyObject *
getattr_by_name(PyObject *self, PyObject *args)
{
  char *name;
  UNLESS(PyArg_Parse(args,"s",&name)) return NULL;
  return self->ob_type->tp_getattr(self,name);
}

static PyObject *
setattr_by_name(PyObject *self, PyObject *args)
{
  char *name;
  PyObject *v;
  UNLESS(PyArg_Parse(args,"sO",&name,&v)) return NULL;
  UNLESS(-1 != self->ob_type->tp_setattr(self,name,v)) return NULL;
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
getattro_by_name(PyObject *self, PyObject *args)
{
  PyObject *name;
  UNLESS(PyArg_Parse(args,"O",&name)) return NULL;
  return self->ob_type->tp_getattro(self,name);
}

static PyObject *
setattro_by_name(PyObject *self, PyObject *args)
{
  PyObject *name;
  PyObject *v;
  UNLESS(PyArg_Parse(args,"OO",&name,&v)) return NULL;
  UNLESS(-1 != self->ob_type->tp_setattro(self,name,v)) return NULL;
  Py_INCREF(Py_None);
  return Py_None;
}
  
static PyObject * 
length_by_name(PyObject *self, PyObject *args)
{ 
  long r; 
  UNLESS(PyArg_Parse(args,"")) return NULL; 
  if(self->ob_type->tp_as_sequence)
    {
      UNLESS(-1 != (r=self->ob_type->tp_as_sequence->sq_length(self)))
	return NULL;
    }
  else
    {
      UNLESS(-1 != (r=self->ob_type->tp_as_mapping->mp_length(self)))
	return NULL;
    }
  return PyInt_FromLong(r); 
} 
  
static PyObject * 
getitem_by_name(PyObject *self, PyObject *args)
{ 
  PyObject *key;
  
  UNLESS(PyArg_Parse(args,"O",&key)) return NULL; 
  if(self->ob_type->tp_as_mapping)
    return self->ob_type->tp_as_mapping->mp_subscript(self,key);
  else
    {
      int index;
      UNLESS(-1 != (index=PyInt_AsLong(key))) return NULL;
      return self->ob_type->tp_as_sequence->sq_item(self,index);
    }
} 

static PyCFunction item_by_name=(PyCFunction)getitem_by_name;
static PyCFunction subscript_by_name=(PyCFunction)getitem_by_name;
  
static PyObject *
setitem_by_name(PyObject *self, PyObject *args)
{ 
  PyObject *key, *v;
  long r;
  
  UNLESS(PyArg_Parse(args,"OO",&key,&v)) return NULL; 
  if(self->ob_type->tp_as_mapping)
    r=self->ob_type->tp_as_mapping->mp_ass_subscript(self,key,v);
  else
    {
      int index;
      UNLESS(-1 != (index=PyInt_AsLong(key))) return NULL;
      r=self->ob_type->tp_as_sequence->sq_ass_item(self,index,v);
    }
  if(r < 0) return NULL;
  Py_INCREF(Py_None);
  return Py_None;
}

static PyCFunction ass_item_by_name=(PyCFunction)setitem_by_name;
static PyCFunction ass_subscript_by_name=(PyCFunction)setitem_by_name;

static PyObject *
slice_by_name(PyObject *self, PyObject *args)
{
  int i1,i2;

  UNLESS(PyArg_Parse(args,"ii",&i1,&i2)) return NULL;
  return self->ob_type->tp_as_sequence->sq_slice(self,i1,i2);
}

static PyObject *
ass_slice_by_name(PyObject *self, PyObject *args)
{
  int i1,i2;
  PyObject *v;
  long r;

  UNLESS(PyArg_Parse(args,"iiO",&i1,&i2,&v)) return NULL;
  r=self->ob_type->tp_as_sequence->sq_ass_slice(self,i1,i2,v);
  if(r<0) return NULL;
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
concat_by_name(PyObject *self, PyObject *args)
{
  PyObject *other;
  UNLESS(PyArg_Parse(args,"O",&other)) return NULL;
  return self->ob_type->tp_as_sequence->sq_concat(self,other);
}

static PyObject *
repeat_by_name(PyObject *self, PyObject *args)
{
  int r;
  UNLESS(PyArg_Parse(args,"i",&r)) return NULL;
  return self->ob_type->tp_as_sequence->sq_repeat(self,r);
}

#define BINOP(OP,AOP) \
static PyObject * \
OP ## _by_name(PyObject *self, PyObject *args) { \
  PyObject *v; \
  UNLESS(PyArg_Parse(args,"O",&v)) return NULL; \
  return PyNumber_ ## AOP(self,v); \
}

BINOP(add,Add)
BINOP(subtract,Subtract)
BINOP(multiply,Multiply)
BINOP(divide,Divide)
BINOP(remainder,Remainder)
BINOP(divmod,Divmod)

static PyObject *
power_by_name(PyObject *self, PyObject *args)
{
  PyObject *v, *z=NULL;
  UNLESS(PyArg_ParseTuple(args,"O|O",&v,&z)) return NULL; 
  return self->ob_type->tp_as_number->nb_power(self,v,z);
}

#define UNOP(OP) \
static PyObject * \
OP ## _by_name(PyObject *self, PyObject *args) { \
  UNLESS(PyArg_Parse(args,"")) return NULL; \
  return self->ob_type->tp_as_number->nb_ ## OP(self); \
}

UNOP(negative)
UNOP(positive)
UNOP(absolute)

static PyObject * 
nonzero_by_name(PyObject *self, PyObject *args) { 
  long r; 
  UNLESS(PyArg_Parse(args,"")) return NULL; 
  UNLESS(-1 != (r=self->ob_type->tp_as_number->nb_nonzero(self))) return NULL; 
  return PyInt_FromLong(r); 
} 

UNOP(invert)

BINOP(lshift,Lshift)
BINOP(rshift,Rshift)
BINOP(and,And)
BINOP(or,Or)
BINOP(xor,Xor)

static PyObject *
coerce_by_name(PyObject *self, PyObject *args)
{
  PyObject *v;
  int r;
  UNLESS(PyArg_Parse(args,"O", &v)) return NULL;
  UNLESS(-1 != (r=self->ob_type->tp_as_number->nb_coerce(&self,&v)))
    {
      Py_INCREF(Py_None);
      return Py_None;
    }
  args=Py_BuildValue("OO",self,v);
  Py_DECREF(self);
  Py_DECREF(v);
  return args;
} 

UNOP(long)
UNOP(int)
UNOP(float)
UNOP(oct)
UNOP(hex)

#define FILLENTRY(T,MN,N,F,D) if(T ## _ ## MN) { \
  UNLESS(-1 != PyMapping_SetItemString(dict,"__" # N "__", \
    newCMethod(type, NULL, "__" # N "__", \
               (PyCFunction)MN ## _by_name, F, # D))) \
    goto err; }

static PyObject *
getBaseDictionary(PyExtensionClass *type)
{
  PyNumberMethods *nm;
  PySequenceMethods *sm;
  PyMappingMethods *mm;
  PyObject *dict;

  UNLESS(dict=type->class_dictionary)
    UNLESS(dict=PyDict_New()) return NULL;
  
  FILLENTRY(type->tp, repr, repr, 0, "convert to an expression string");
  FILLENTRY(type->tp, hash, hash, 0, "compute a hash value");
  FILLENTRY(type->tp, call, call, 2, "call as a function");
  FILLENTRY(type->tp, compare, comp, 0, "compare with another object");
  FILLENTRY(type->tp, getattr, getattr, 0, "Get an attribute");
  FILLENTRY(type->tp, setattr, setattr, 0, "Set an attribute");
  FILLENTRY(type->tp, getattro, getattr, 0, "Get an attribute");
  FILLENTRY(type->tp, setattro, setattr, 0, "Set an attribute");

  if(sm=type->tp_as_sequence)
    {
      FILLENTRY(sm->sq, length, len, 0, "Get the object length");
      FILLENTRY(sm->sq, concat, concat, 0,
		"Concatinate the object with another");
      FILLENTRY(sm->sq, repeat, repeat, 0,
		"Get a new object that is the object repeated.");
      FILLENTRY(sm->sq, item, getitem, 0, "Get an item");
      FILLENTRY(sm->sq, slice, getslice, 0, "Get a slice");
      FILLENTRY(sm->sq, ass_item, setitem, 0, "Assign an item");
      FILLENTRY(sm->sq, ass_slice, setslice, 0, "Assign a slice");
    }      

  if(mm=type->tp_as_mapping)
    {
      FILLENTRY(mm->mp, length, len, 0, "Get the object length");
      FILLENTRY(mm->mp, subscript, getitem, 0, "Get an item");
      FILLENTRY(mm->mp, ass_subscript, setitem, 0, "Assign an item");
    }      

  if((nm=type->tp_as_number) != NULL)
    {
      FILLENTRY(nm->nb, add, add, 0, "Add to another");
      FILLENTRY(nm->nb, subtract, sub, 0, "Subtract another");
      FILLENTRY(nm->nb, multiply, mul, 0, "Multiple by another");
      FILLENTRY(nm->nb, divide, div, 0, "Divide by another");
      FILLENTRY(nm->nb, remainder, mod, 0, "Compute a remainder");
      FILLENTRY(nm->nb, power, pow, 1, "Raise to a power");
      FILLENTRY(nm->nb, divmod, divmod, 0,
		"Compute the whole result and remainder of dividing\n"
		"by another");
      FILLENTRY(nm->nb, negative, neg, 0, "Get the negative value.");
      FILLENTRY(nm->nb, positive, pos, 0, "Compute positive value");
      FILLENTRY(nm->nb, absolute, abs, 0, "Compute absolute value");
      FILLENTRY(nm->nb, nonzero, nonzero, 0, "Determine whether nonzero");
      FILLENTRY(nm->nb, invert, inv, 0, "Compute inverse");
      FILLENTRY(nm->nb, lshift, lshift, 0, "Shist left");
      FILLENTRY(nm->nb, rshift, rshift, 0, "Shist right");
      FILLENTRY(nm->nb, and, and, 0, "bitwize logical and");
      FILLENTRY(nm->nb, or, or, 0, "bitwize logical or");
      FILLENTRY(nm->nb, xor, xor, 0, "bitwize logical excusive or");
      FILLENTRY(nm->nb, coerce, coerce, 0,
		"Coerce woth another to a common type");
      FILLENTRY(nm->nb, int, int, 0, "Convert to an integer");
      FILLENTRY(nm->nb, long, long, 0,
		"Convert to an infinite-precision integer");
      FILLENTRY(nm->nb, float, float, 0, "Convert to floating point number");
      FILLENTRY(nm->nb, oct, oct, 0, "Convert to an octal string");
      FILLENTRY(nm->nb, hex, hex, 0, "Convert to a hexadecimal string");
    }
  return dict;
err:
  Py_DECREF(dict);
  return NULL;
}

#undef UNARY_OP
#undef BINOP
#undef UNOP
#undef FILLENTRY

PyObject *
EC_reduce(PyObject *self, PyObject *args)
{
  PyObject *state=0;

  if(args=PyObject_GetAttr(self,py__getinitargs__))
    {
      UNLESS_ASSIGN(args,PyEval_CallObject(args,NULL)) return NULL;
      UNLESS_ASSIGN(args,PySequence_Tuple(args)) return NULL;
    }
  else
    {
      PyErr_Clear();
      args=PyTuple_New(0);
    }

  if(state=PyObject_GetAttr(self,py__getstate__))
    {
      UNLESS_ASSIGN(state,PyEval_CallObject(state,NULL)) goto err;
      ASSIGN(args,Py_BuildValue("OOO", self->ob_type, args, state));
      Py_DECREF(state);
    }
  else
    {
      PyErr_Clear();

      if(state=PyObject_GetAttr(self, py__dict__))
	{
	  ASSIGN(args,Py_BuildValue("OOO", self->ob_type, args, state));
	  Py_DECREF(state);
	}
      else
	{
	  PyErr_Clear();
	  ASSIGN(args, Py_BuildValue("OO", self->ob_type, args));
	}
    }

  return args;

err:
  Py_DECREF(args);
  return NULL;
}

static PyObject *
inheritedAttribute(PyExtensionClass *self, PyObject *name)
{
  UNLESS(name) return PyErr_Format(PyExc_TypeError,
				   "expected one argument, and none given",
				   NULL);
  return CCL_getattr(self,name,1);
}

static PyObject *
inheritedClassAttribute(PyExtensionClass *self, PyObject *name)
{
  UNLESS(name) return PyErr_Format(PyExc_TypeError,
				   "expected one argument, and none given",
				   NULL);
  UNLESS(name=PySequence_Concat(pyclass_,name)) return NULL;
  UNLESS_ASSIGN(name,CCL_getattr(self,name,1)) return NULL;
  if(UnboundPMethod_Check(name))
    ASSIGN(name,bindPMethod((PMethod*)name,(PyObject*)self));
  return name;
}

struct PyMethodDef ECI_methods[] = {
  {"__reduce__",(PyCFunction)EC_reduce,0,
   "__reduce__() -- Reduce an instance into it's class and creation data"
  },
  {NULL,		NULL}		/* sentinel */
};

static PyObject *
initializeBaseExtensionClass(PyExtensionClass *self)
{
  PyMethodChain *chain, top = { ECI_methods, NULL };
  PyObject *dict;

  self->ob_type=(PyTypeObject*)&ECType;
  Py_INCREF(self->ob_type);

  UNLESS(dict=self->class_dictionary=getBaseDictionary(self)) return NULL;

  if(self->tp_name)
    {
      PyObject *name;

      UNLESS(name=PyString_FromString(self->tp_name)) goto err;
      if(0 > PyMapping_SetItemString(dict,"__doc__",name)) goto err;
      Py_DECREF(name);
    }
  else if(0 > PyMapping_SetItemString(dict,"__doc__",Py_None)) goto err;

  top.link=&(self->methods);
  
  chain=&top;
  while (chain != NULL)
    {
      PyMethodDef *ml = chain->methods;
      for (; ml && ml->ml_name != NULL; ml++) 
	{
	  if(ml->ml_meth)
	    {
	      UNLESS(-1 != PyMapping_SetItemString(
                               dict,ml->ml_name,
			       newCMethod(self, NULL, 
					  ml->ml_name,
					  ml->ml_meth,
					  ml->ml_flags,
					  ml->ml_doc)))
		return NULL;
	    }
	  else if(ml->ml_doc && *(ml->ml_doc))
	    {
	      /* No actual meth, this is probably to hook a doc string
		 onto a special method. */
	      PyObject *m;

	      if(m=PyMapping_GetItemString(dict,ml->ml_name))
		{
		  if(m->ob_type==&CMethodType)
		    ((CMethod *)(m))->doc=ml->ml_doc;
		}
	      else
		PyErr_Clear();
	    }
	}
      chain=chain->link;
    }
  return (PyObject*)self;

err:
  Py_DECREF(dict);
  return NULL;
}

static void
CCL_dealloc(PyExtensionClass *self)
{
#ifdef TRACE_DEALLOC
  fprintf(stderr,"Deallocating %s\n", self->tp_name);
#endif
  Py_XDECREF(self->class_dictionary);
  if(self->bases)
    {
      /* If we are a subclass, then we strduped our name */
      free(self->tp_name);

      /* And we allocated our own protocol structures */
      if(self->tp_as_number)   free(self->tp_as_number);
      if(self->tp_as_sequence) free(self->tp_as_sequence);
      if(self->tp_as_mapping)  free(self->tp_as_mapping);
      
      Py_DECREF(self->bases);
    }
  Py_XDECREF(self->ob_type);
  PyMem_DEL(self);
}
  
static PyObject *
ExtensionClass_FindInstanceAttribute(PyObject *inst, PyObject *oname,
				     char *name)
{
  /* Look up an attribute for an instance from:

     The instance dictionary,
     The class dictionary, or
     The base objects.
   */
  PyObject *r=0;
  PyExtensionClass *self;

  if(! name) return NULL;

  self=(PyExtensionClass*)(inst->ob_type);

  if(*name=='_' && name[1]=='_')
    {
      char *n=name+2;
      if(*n == 'c' && strcmp(n,"class__")==0)
	{
	  Py_INCREF(self);
	  return (PyObject*)self;
	}
      if(self->bases && *n=='d' && strcmp(n,"dict__")==0)
	{
	  r = INSTANCE_DICT(inst);
	  Py_INCREF(r);
	  return r;
	}
    }

  if(self->bases)
    {
      r= INSTANCE_DICT(inst);
      if((r = PyObject_GetItem(r,oname)) && NeedsToBeBound(r))
	{
	  ASSIGN(r, CallMethodO(r, py__of__, Build("(O)", inst), NULL));
	  UNLESS(r) return NULL;
	}
    }
  UNLESS(r)
    {
      PyErr_Clear();
      UNLESS(r=CCL_getattr(self,oname,0)) return NULL;

      /* We got something from our class, maybe its an unbound method. */
      if(UnboundCMethod_Check(r))
	ASSIGN(r,(PyObject*)bindCMethod((CMethod*)r,inst));
      else if(UnboundPMethod_Check(r))
	ASSIGN(r,bindPMethod((PMethod*)r,inst));
    }
      
  return r;
}

static PyObject *
EC_findiattrs(PyObject *self, char *name)
{
  PyObject *s, *r;

  UNLESS(s=PyString_FromString(name)) return NULL;
  r=ExtensionClass_FindInstanceAttribute(self,s,name);
  Py_DECREF(s);
  return r;
}
  
static PyObject *
EC_findiattro(PyObject *self, PyObject *name)
{
  return ExtensionClass_FindInstanceAttribute(self,name,
					      PyString_AsString(name));
}

static int
subclass_simple_setattr(PyObject *self, char *name, PyObject *v);

static PyObject *
CCL_getattr(PyExtensionClass *self, PyObject *oname, int look_super)
{
  PyObject *r=0;

  if(! look_super) r=PyObject_GetItem(self->class_dictionary,oname);
  UNLESS(r)
    {
      if(self->bases)
	{
	  int n, i;
	  PyObject *c;
	  
	  n=PyTuple_Size(self->bases);
	  for(i=0; i < n; i++)
	    {
	      PyErr_Clear();
	      c=PyTuple_GET_ITEM(self->bases, i);
	      if(ExtensionClass_Check(c))
		r=CCL_getattr(AsExtensionClass(c),oname,0);
	      else
		r=PyObject_GetAttr(c,oname);
	      if(r) break;
	    }
	}
      UNLESS(r)
	{
	  PyObject *t, *v, *tb;

	  PyErr_Fetch(&t,&v,&tb);
	  if(t==PyExc_KeyError && PyObject_Compare(v,oname) == 0)
	    {
	      Py_DECREF(t);
	      t=PyExc_AttributeError;
	      Py_INCREF(t);
	    }
	  PyErr_Restore(t,v,tb);	  
	  return NULL;
	}
    }

  if(PyFunction_Check(r) || NeedsToBeBound(r))
    {
      UNLESS_ASSIGN(r,newPMethod(self,r)) return NULL;
    }
  else if(PyMethod_Check(r) && ! PyMethod_Self(r))
    {
      UNLESS_ASSIGN(r,newPMethod(self, PyMethod_Function(r)))
	return NULL;
    }

  return r;
}

static PyObject *
CCL_reduce(PyExtensionClass *self, PyObject *args)
{
  return PyString_FromString(self->tp_name);
}

PyObject *
CCL_getattro(PyExtensionClass *self, PyObject *name)
{
  char *n, *nm=0;
  PyObject *r;

  if(PyString_Check(name) && (n=nm=PyString_AS_STRING((PyStringObject*)name)))
    {
      if(*n=='_' && *++n=='_')
	{
	  switch (*++n)
	    {
	    case 's':
	      if(strcmp(n,"safe_for_unpickling__")==0)
		return PyInt_FromLong(1);
	      break;
	    case 'n':
	      if(strcmp(n,"name__")==0)
		return PyString_FromString(self->tp_name);
	      break;
	    case 'r':
	      if(strcmp(n,"reduce__")==0)
		return newCMethod(self,(PyObject*)self,
		   "__reduce__",(PyCFunction)CCL_reduce,0,
		   "__reduce__() -- Reduce the class to a class name");
	      break;
	    case 'd':
	      if(strcmp(n,"dict__")==0)
		{
		  Py_INCREF(self->class_dictionary);
		  return self->class_dictionary;
		}
	      break;
	    case 'b':
	      if(strcmp(n,"bases__")==0)
		{
		  if(self->bases)
		    {
		      Py_INCREF(self->bases);
		      return self->bases;
		    }
		  else
		    return PyTuple_New(0);
		}
	      break;
	    }
	}
    }

  if(strcmp(nm,"inheritedAttribute")==0)
    {
      return newCMethod(self,(PyObject*)self,
			"inheritedAttribute",(PyCFunction)inheritedAttribute,0,
			"look up an attribute in a class's super classes");
    }

  if(nm && *nm++=='c' && *nm++=='l' && *nm++=='a' && *nm++=='s' && *nm++=='s'
     && *nm=='_')
    {
      UNLESS(r=CCL_getattr(self,name,0)) return NULL;
      if(UnboundPMethod_Check(r))
	ASSIGN(r,bindPMethod((PMethod*)r,(PyObject*)self));
      return r;
    }
  
  if(r=CCL_getattr(self,name,0)) return r;

  return NULL;
}

static int
CCL_setattro(PyExtensionClass *self, PyObject *name, PyObject *v)
{
  if(v && UnboundCMethod_Check(v))
    {
      char *n;
      PyNumberMethods *nm;
      PySequenceMethods *s, *ms;
      PyMappingMethods *m, *mm;

      UNLESS(n=PyString_AsString(name)) return -1;
      if(*n=='_' && n[1]=='_')
	{
	  n+=2;

#define SET_SPECIAL(C,P) \
	  if(strcmp(n,#P "__")==0 \
	     && AsCMethod(v)->meth==(PyCFunction)C ## _by_name \
	     && Subclass_Check(self,AsCMethod(v)->type)) { \
	      self->tp_ ## C=AsCMethod(v)->type->tp_ ## C; \
	      return PyObject_SetItem(self->class_dictionary, name, v); }
	  /*
	  SET_SPECIAL(setattr,setattr);
	  SET_SPECIAL(setattro,setattr);
	  */
	  SET_SPECIAL(compare,cmp);
	  SET_SPECIAL(hash,hash);
	  SET_SPECIAL(repr,repr);
	  SET_SPECIAL(call,call);
	  SET_SPECIAL(str,str);
#undef SET_SPECIAL

#define SET_SPECIAL(C,P) \
	  if(strcmp(n,#P "__")==0 && AsCMethod(v)->meth==C ## _by_name \
	     && Subclass_Check(self,AsCMethod(v)->type) \
	     && (nm=self->tp_as_number)) { \
	      nm->nb_ ## C=AsCMethod(v)->type->tp_as_number->nb_ ## C; \
	      return PyObject_SetItem(self->class_dictionary, name, v); } 
	  SET_SPECIAL(add,add);
	  SET_SPECIAL(subtract,sub);
	  SET_SPECIAL(multiply,mult);
	  SET_SPECIAL(divide,div);
	  SET_SPECIAL(remainder,mod);
	  SET_SPECIAL(power,pow);
	  SET_SPECIAL(divmod,divmod);
	  SET_SPECIAL(lshift,lshift);
	  SET_SPECIAL(rshift,rshift);
	  SET_SPECIAL(and,and);
	  SET_SPECIAL(or,or);
	  SET_SPECIAL(xor,xor);
	  SET_SPECIAL(coerce,coerce);
	  SET_SPECIAL(negative,neg);
	  SET_SPECIAL(positive,pos);
	  SET_SPECIAL(absolute,abs);
	  SET_SPECIAL(nonzero,nonzero);
	  SET_SPECIAL(invert,inv);
	  SET_SPECIAL(int,int);
	  SET_SPECIAL(long,long);
	  SET_SPECIAL(float,float);
	  SET_SPECIAL(oct,oct);
	  SET_SPECIAL(hex,hex);
#undef SET_SPECIAL

	  if(strcmp(n,"len__")==0 && AsCMethod(v)->meth==length_by_name 
	     && Subclass_Check(self,AsCMethod(v)->type))
	     {
	       if((s=self->tp_as_sequence) &&
		  (ms=AsCMethod(v)->type->tp_as_sequence) &&
		  ms->sq_length)
		 s->sq_length=ms->sq_length;
	       if((m=self->tp_as_mapping) &&
		  (mm=AsCMethod(v)->type->tp_as_mapping) &&
		  mm->mp_length)
		 m->mp_length=mm->mp_length;
	       return PyObject_SetItem(self->class_dictionary, name, v);
	     } 

	  if(strcmp(n,"getitem__")==0 && AsCMethod(v)->meth==getitem_by_name 
	     && Subclass_Check(self,AsCMethod(v)->type))
	     {
	       if((s=self->tp_as_sequence) &&
		  (ms=AsCMethod(v)->type->tp_as_sequence) &&
		  ms->sq_item)
		 s->sq_item=ms->sq_item;
	       if((m=self->tp_as_mapping) &&
		  (mm=AsCMethod(v)->type->tp_as_mapping) &&
		  mm->mp_subscript)
		 m->mp_subscript=mm->mp_subscript;
	       return PyObject_SetItem(self->class_dictionary, name, v);
	     } 

	  if(strcmp(n,"setitem__")==0 &&
	     AsCMethod(v)->meth==(PyCFunction)setitem_by_name 
	     && Subclass_Check(self,AsCMethod(v)->type))
	     {
	       if((s=self->tp_as_sequence) &&
		  (ms=AsCMethod(v)->type->tp_as_sequence) &&
		  ms->sq_ass_item)
		 s->sq_ass_item=ms->sq_ass_item;
	       if((m=self->tp_as_mapping) &&
		  (mm=AsCMethod(v)->type->tp_as_mapping) &&
		  mm->mp_ass_subscript)
		 m->mp_ass_subscript=mm->mp_ass_subscript;
	       return PyObject_SetItem(self->class_dictionary, name, v);
	     } 

#define SET_SPECIAL(C,P) \
	  if(strcmp(n,#P "__")==0 \
	     && AsCMethod(v)->meth==(PyCFunction)C ## _by_name \
	     && Subclass_Check(self,AsCMethod(v)->type) \
	     && (s=self->tp_as_sequence)) { \
	      s->sq_ ## C=AsCMethod(v)->type->tp_as_sequence->sq_ ## C; \
	      return PyObject_SetItem(self->class_dictionary, name, v); } 
	  SET_SPECIAL(slice,getslice);
	  SET_SPECIAL(ass_slice,setslice);
	  SET_SPECIAL(concat,concat);
	  SET_SPECIAL(repeat,repeat);
#undef SET_SPECIAL

	}
    }
  return PyObject_SetItem(self->class_dictionary, name, v);
}

static PyObject *
CCL_call(PyExtensionClass *self, PyObject *arg, PyObject *kw)
{
  PyObject *inst=0, *init=0, *args=0;
  typedef struct { PyObject_VAR_HEAD } PyVarObject__;

  if(! self->tp_dealloc)
    {
      PyErr_SetString(PyExc_TypeError,
		      "Attempt to create instance of an abstract type");
      return NULL;
    }

  if(self->tp_itemsize)
    {
      /* We have a variable-sized object, we need to get it's size */
      PyObject *var_size;
      int size;
      
      if(var_size=CCL_getattr(self,py__var_size__, 0))
	{
	  UNLESS_ASSIGN(var_size,PyObject_CallObject(var_size,arg))
	    return NULL;
	}
      else
	{
	  UNLESS(-1 != (size=PyTuple_Size(arg))) return NULL;
	  if(size > 0)
	    {
	      var_size=PyTuple_GET_ITEM(arg, 0);
	      if(PyInt_Check(var_size))
		size=PyInt_AsLong(var_size);
	      else
		size=-1;
	    }
	  else
	    size=-1;
	  if(size < 0)
	    {
	      PyErr_SetString(PyExc_TypeError,
			      "object size expected as first argument");
	      return NULL;
	    }
	}
      UNLESS(inst=PyObject_NEW_VAR(PyObject,(PyTypeObject *)self, size))
	return NULL;
      memset(inst,0,self->tp_basicsize+self->tp_itemsize*size);
      inst->ob_refcnt=1;
      inst->ob_type=(PyTypeObject *)self;
      ((PyVarObject__*)inst)->ob_size=size;
    }
  else
    {
      UNLESS(inst=PyObject_NEW(PyObject,(PyTypeObject *)self)) return NULL;
      memset(inst,0,self->tp_basicsize);
      inst->ob_refcnt=1;
      inst->ob_type=(PyTypeObject *)self;
    }

  Py_INCREF(self);
  if(self->bases)
    {
      UNLESS(INSTANCE_DICT(inst)=PyDict_New()) goto err;
    }

  if(init=CCL_getattr(self,py__init__,0))
    {
      UNLESS(args=Py_BuildValue("(O)",inst)) goto err;
      if(arg) UNLESS_ASSIGN(args,PySequence_Concat(args,arg)) goto err;
      UNLESS_ASSIGN(args,PyEval_CallObjectWithKeywords(init,args,kw)) goto err;
      Py_DECREF(args);
      Py_DECREF(init);
    }
  else PyErr_Clear();

  return inst;
err:
  Py_DECREF(inst);
  Py_XDECREF(init);
  Py_XDECREF(args);
  return NULL;
}

static PyObject *
CCL_repr(PyExtensionClass *self)
{
  char p[128];

  sprintf(p,"%p",self);
  return PyString_Build("<extension class %s at %s>","ss",
			self->tp_name, p);
}

static PyTypeObject ECTypeType = {
  PyObject_HEAD_INIT(NULL)
  0,				/*ob_size*/
  "ExtensionClass Class",	/*tp_name*/
  sizeof(PyExtensionClass),    	/*tp_basicsize*/
  0,				/*tp_itemsize*/
  /* methods */
  (destructor)CCL_dealloc,	/*tp_dealloc*/
  (printfunc)0,			/*tp_print*/
  (getattrfunc)0,		/*tp_getattr*/
  (setattrfunc)0,		/*tp_setattr*/
  (cmpfunc)0,			/*tp_compare*/
  (reprfunc)CCL_repr,		/*tp_repr*/
  0,				/*tp_as_number*/
  0,				/*tp_as_sequence*/
  0,				/*tp_as_mapping*/
  (hashfunc)0,			/*tp_hash*/
  (ternaryfunc)CCL_call,       	/*tp_call*/
  (reprfunc)0,			/*tp_str*/
  (getattrofunc)CCL_getattro,	/*tp_getattr with object key*/
  (setattrofunc)CCL_setattro,	/*tp_setattr with object key*/
  /* Space for future expansion */
  0L,0L,
  "Class of C classes" /* Documentation string */
};

/* End of code for ExtensionClass objects */
/* -------------------------------------------------------- */

/* subclassing code: */
  
static PyObject *
subclass_getspecial(PyObject *inst, PyObject *oname)
{
  PyObject *r=0;
  PyExtensionClass *self;

  self=(PyExtensionClass*)(inst->ob_type);
  r= INSTANCE_DICT(inst);
  r = PyObject_GetItem(r,oname);
  UNLESS(r)
    {
      PyErr_Clear();
      r=CCL_getattr(self,oname,0);
    }
      
  return r;
}

static PyObject *
subclass_getattro(PyObject *self, PyObject *name)
{
  PyObject *r;

  if(! name) return NULL;
  UNLESS(r=EC_findiattro(self,name))
    {
      PyErr_Clear();
      r=EC_findiattro(self,py__getattr__);
      if(r) ASSIGN(r,PyObject_CallFunction(r,"O",name));
    }
  return r;
}

static int
subclass_simple_setattro(PyObject *self, PyObject *name, PyObject *v)
{
  if(v)
    return PyDict_SetItem(INSTANCE_DICT(self),name,v);
  else
    return PyDict_DelItem(INSTANCE_DICT(self),name);
}

static int
subclass_simple_setattr(PyObject *self, char *name, PyObject *v)
{
  if(v)
    return PyDict_SetItemString(INSTANCE_DICT(self),name,v);
  else
    return PyDict_DelItemString(INSTANCE_DICT(self),name);
}

static int 
subclass_setattr(PyObject *self, PyObject *oname, char *name, PyObject *v)
{
  PyObject *m=0, *et, *ev, *etb;

  if(! name) return -1;

  if(!v && (m=subclass_getspecial(self,py__delattr__)))
    {
      if(UnboundEMethod_Check(m))
	{
	  UNLESS_ASSIGN(m,PyObject_CallFunction(m,"OO",self,oname)) return -1;
	}
      else UNLESS_ASSIGN(m,PyObject_CallFunction(m,"O",oname)) return -1;
      Py_DECREF(m);
      return 0;
    }

  UNLESS(m=subclass_getspecial(self,py__setattr__))
    goto default_setattr;
  if(UnboundCMethod_Check(m) && AsCMethod(m)->meth==setattr_by_name
     && SubclassInstance_Check(self,AsCMethod(m)->type))
    {
      UNLESS(-1 != AsCMethod(m)->type->tp_setattr(self,name,v))
	goto dictionary_setattr;
      return 0;
    }
  else 
    if(UnboundCMethod_Check(m) && AsCMethod(m)->meth==setattro_by_name
       && SubclassInstance_Check(self,AsCMethod(m)->type))
      {
	UNLESS(-1 != AsCMethod(m)->type->tp_setattro(self,oname,v))
	  goto dictionary_setattr;
	return 0;
      }
  if(! v) goto default_setattr;
  if(UnboundEMethod_Check(m))
    {
      UNLESS_ASSIGN(m,PyObject_CallFunction(m,"OOO",self,oname,v)) return -1;
    }
  else UNLESS_ASSIGN(m,PyObject_CallFunction(m,"OO",oname,v)) return -1;
  Py_DECREF(m);
  return 0;

dictionary_setattr:

  Py_XDECREF(m);

  PyErr_Fetch(&et, &ev, &etb);
  if(et==PyExc_AttributeError)
    {
      char *s;
      
      if(ev && PyString_Check(ev) && (s=PyString_AsString(ev)) &&
	 strcmp(s,name)==0)
	{
	  Py_XDECREF(et);
	  Py_XDECREF(ev);
	  Py_XDECREF(etb);
	  et=0;
	}
    }
  if(et)
    {
      PyErr_Restore(et,ev,etb);
      return -1;
    }	
  
default_setattr:

  PyErr_Clear();
  
  return subclass_simple_setattro(self, oname, v);
}

static int
subclass_setattro(PyObject *self, PyObject *name, PyObject *v)
{
  return subclass_setattr(self,name,PyString_AsString(name),v);
}


static int
subclass_compare(PyObject *self, PyObject *v)
{
  PyObject *m;
  long r;

  UNLESS(m=subclass_getspecial(self,py__cmp__)) return -1;
  if(UnboundCMethod_Check(m) && AsCMethod(m)->meth==compare_by_name
     && SubclassInstance_Check(self,AsCMethod(m)->type))
    r=AsCMethod(m)->type->tp_compare(self,v);
  else
    {
      if(UnboundEMethod_Check(m))
	{
	  UNLESS_ASSIGN(m,PyObject_CallFunction(m,"OO",self,v))
	    return -1;
	}
      else UNLESS_ASSIGN(m,PyObject_CallFunction(m,"O",v)) return -1;
      r=PyInt_AsLong(m);
    }
  Py_DECREF(m);
  return r;
}  

static long
subclass_hash(PyObject *self)
{
  PyObject *m;
  long r;

  UNLESS(m=subclass_getspecial(self,py__hash__)) return -1;
  if(UnboundCMethod_Check(m) && AsCMethod(m)->meth==hash_by_name
     && SubclassInstance_Check(self,AsCMethod(m)->type))
    r=AsCMethod(m)->type->tp_hash(self);
  else
    {
      if(UnboundEMethod_Check(m))
	{
	  UNLESS_ASSIGN(m,PyObject_CallFunction(m,"O",self))
	    return -1;
	}
      else UNLESS_ASSIGN(m,PyObject_CallFunction(m,"")) return -1;
      r=PyInt_AsLong(m);
    }
  Py_DECREF(m);
  return r;
}  

static PyObject *
default_subclass_repr(PyObject *self)
{
  char p[64];
  
  PyErr_Clear();
  sprintf(p,"%p",self);
  return PyString_Build("<%s instance at %s>","ss",
			self->ob_type->tp_name, p);
}

static PyObject *
subclass_repr(PyObject *self)
{
  PyObject *m;

  UNLESS(m=subclass_getspecial(self,py__repr__))
    return default_subclass_repr(self);

  if(UnboundCMethod_Check(m) && AsCMethod(m)->meth==repr_by_name
     && SubclassInstance_Check(self,AsCMethod(m)->type))
    ASSIGN(m,AsCMethod(m)->type->tp_repr(self));
  else if(UnboundEMethod_Check(m))
    ASSIGN(m,PyObject_CallFunction(m,"O",self));
  else
    ASSIGN(m,PyObject_CallFunction(m,""));
  return m;
}  

static PyObject *
subclass_call(PyObject *self, PyObject *args, PyObject *kw)
{
  PyObject *m;

  UNLESS(m=subclass_getspecial(self,py__call__)) return NULL;
  if(UnboundCMethod_Check(m) && AsCMethod(m)->meth==(PyCFunction)call_by_name
     && SubclassInstance_Check(self,AsCMethod(m)->type))
    ASSIGN(m,AsCMethod(m)->type->tp_call(self,args,kw));
  else
    {
      if(UnboundEMethod_Check(m))
	{
	  PyObject *a;
	  a=Py_BuildValue("(O)",self);
	  if(a) ASSIGN(a,PySequence_Concat(a,args));
	  if(a) ASSIGN(m,PyEval_CallObjectWithKeywords(m,a,kw));
	  else  ASSIGN(m,NULL);
	  Py_XDECREF(a);
	}
      else
	ASSIGN(m,PyEval_CallObjectWithKeywords(m,args,kw));
    }
  return m;
}  

static PyObject *
subclass_str(PyObject *self)
{
  PyObject *m;

  UNLESS(m=subclass_getspecial(self,py__str__))
    {
      PyErr_Clear();
      return subclass_repr(self);
    }
  if(UnboundCMethod_Check(m) && AsCMethod(m)->meth==str_by_name
     && SubclassInstance_Check(self,AsCMethod(m)->type))
    ASSIGN(m,AsCMethod(m)->type->tp_str(self));
  else if(UnboundEMethod_Check(m))
    ASSIGN(m,PyObject_CallFunction(m,"O",self));
  else
    ASSIGN(m,PyObject_CallFunction(m,""));
  return m;
}  

#define BINSUB(M,N,A) \
static PyObject * \
subclass_ ## M(PyObject *self, PyObject *v) \
{ \
  PyObject *m; \
  UNLESS(m=subclass_getspecial(self,py__ ## N ## __)) return NULL; \
  if(UnboundCMethod_Check(m) && AsCMethod(m)->meth==M ## _by_name \
     && SubclassInstance_Check(self,AsCMethod(m)->type)) \
    ASSIGN(m,PyNumber_ ## A(self,v)); \
  else if(UnboundEMethod_Check(m)) \
    ASSIGN(m,PyObject_CallFunction(m,"OO",self,v)); \
  else \
    ASSIGN(m,PyObject_CallFunction(m,"O",v)); \
  return m; \
}  
  
BINSUB(add,add,Add)
BINSUB(subtract,sub,Subtract)
BINSUB(multiply,mul,Multiply)
BINSUB(divide,div,Divide)
BINSUB(remainder,mod,Remainder)

static PyObject * 
subclass_power(PyObject *self, PyObject *v, PyObject *w) 
{ 
  PyObject *m; 
  UNLESS(m=subclass_getspecial(self,py__pow__)) return NULL; 
  if(UnboundCMethod_Check(m) && AsCMethod(m)->meth==power_by_name
     && SubclassInstance_Check(self,AsCMethod(m)->type)) 
    ASSIGN(m,AsCMethod(m)->type->tp_as_number->nb_power(self,v,w));
  else if(UnboundEMethod_Check(m))
    ASSIGN(m,PyObject_CallFunction(m,"OOO",self,v,w));
  else
    ASSIGN(m,PyObject_CallFunction(m,"OO",v,w)); 
  return m; 
}  

BINSUB(divmod,divmod,Divmod)
BINSUB(lshift,lshift,Lshift)
BINSUB(rshift,rshift,Rshift)
BINSUB(and,and,And)
BINSUB(or,or,Or)
BINSUB(xor,xor,Xor)


static int
subclass_coerce(PyObject **self, PyObject **v) 
{ 
  PyObject *m; 
  int r;

  UNLESS(m=subclass_getspecial(*self,py__coerce__)) return -1; 
  if(UnboundCMethod_Check(m) && AsCMethod(m)->meth==coerce_by_name
     && SubclassInstance_Check(*self,AsCMethod(m)->type)) 
    r=AsCMethod(m)->type->tp_as_number->nb_coerce(self,v);
  else 
    { 
      if(UnboundEMethod_Check(m))
	{
	  UNLESS_ASSIGN(m,PyObject_CallFunction(m,"OO",*self,v)) return -1;
	}
      UNLESS_ASSIGN(m,PyObject_CallFunction(m,"O",*v)) return -1;
      if(m==Py_None) r=-1;
      else
	{
	  PyArg_ParseTuple(m,"O",v);
	  Py_INCREF(*self);
	  Py_INCREF(*v);
	  r=0;
	}
    } 
  Py_DECREF(m);
  return r; 
}  

#define UNSUB(M,N) \
static PyObject * \
subclass_ ## M(PyObject *self) \
{ \
  PyObject *m; \
  UNLESS(m=subclass_getspecial(self,py__ ## N ## __)) return NULL; \
  if(UnboundCMethod_Check(m) && AsCMethod(m)->meth==M ## _by_name \
     && SubclassInstance_Check(self,AsCMethod(m)->type)) \
    ASSIGN(m,AsCMethod(m)->type->tp_as_number->nb_ ## M(self)); \
  else if(UnboundEMethod_Check(m)) \
    ASSIGN(m,PyObject_CallFunction(m,"O",self)); \
  else \
    ASSIGN(m,PyObject_CallFunction(m,"")); \
  return m; \
}  

UNSUB(negative, neg)
UNSUB(positive, pos)
UNSUB(absolute, abs)

static int
subclass_nonzero(PyObject *self)
{
  PyObject *m;
  long r;

  UNLESS(m=subclass_getspecial(self,py__nonzero__)) return -1;
  if(UnboundCMethod_Check(m) && AsCMethod(m)->meth==nonzero_by_name
     && SubclassInstance_Check(self,AsCMethod(m)->type))
    r=AsCMethod(m)->type->tp_as_number->nb_nonzero(self);
  else
    {
      if(UnboundEMethod_Check(m))
	{
	  UNLESS_ASSIGN(m,PyObject_CallFunction(m,"O",self))
	    return -1;
	}
      else UNLESS_ASSIGN(m,PyObject_CallFunction(m,"")) return -1;
      r=PyInt_AsLong(m);
    }
  Py_DECREF(m);
  return r;
}  

UNSUB(invert, inv)
UNSUB(int, int)
UNSUB(long, long)
UNSUB(float, float)
UNSUB(oct, oct)
UNSUB(hex, hex)

#undef UNSUB
#undef BINSUB


static PyNumberMethods subclass_as_number = {
  (binaryfunc)subclass_add,		/*nb_add*/
  (binaryfunc)subclass_subtract,	/*nb_subtract*/
  (binaryfunc)subclass_multiply,	/*nb_multiply*/
  (binaryfunc)subclass_divide,		/*nb_divide*/
  (binaryfunc)subclass_remainder,	/*nb_remainder*/
  (binaryfunc)subclass_divmod,		/*nb_divmod*/
  (ternaryfunc)subclass_power,		/*nb_power*/
  (unaryfunc)subclass_negative,		/*nb_negative*/
  (unaryfunc)subclass_positive,		/*nb_positive*/
  (unaryfunc)subclass_absolute,		/*nb_absolute*/
  (inquiry)subclass_nonzero,		/*nb_nonzero*/
  (unaryfunc)subclass_invert,		/*nb_invert*/
  (binaryfunc)subclass_lshift,		/*nb_lshift*/
  (binaryfunc)subclass_rshift,		/*nb_rshift*/
  (binaryfunc)subclass_and,		/*nb_and*/
  (binaryfunc)subclass_xor,		/*nb_xor*/
  (binaryfunc)subclass_or,		/*nb_or*/
  (coercion)subclass_coerce,		/*nb_coerce*/
  (unaryfunc)subclass_int,		/*nb_int*/
  (unaryfunc)subclass_long,		/*nb_long*/
  (unaryfunc)subclass_float,		/*nb_float*/
  (unaryfunc)subclass_oct,		/*nb_oct*/
  (unaryfunc)subclass_hex,		/*nb_hex*/
};

static long
subclass_length(PyObject *self)
{
  PyObject *m;
  long r;
  PyExtensionClass *t;

  UNLESS(m=subclass_getspecial(self,py__len__)) return -1;
  if(UnboundCMethod_Check(m) && AsCMethod(m)->meth==length_by_name
     && SubclassInstance_Check(self,AsCMethod(m)->type))
    {
      t=(PyExtensionClass*)AsCMethod(m)->type;
      Py_DECREF(m);
      if(t->tp_as_sequence)
	return t->tp_as_sequence->sq_length(self);
      else
	return t->tp_as_mapping->mp_length(self);
    }
  if(UnboundEMethod_Check(m))
    {
      UNLESS_ASSIGN(m,PyObject_CallFunction(m,"O",self)) return -1;
    }
  else UNLESS_ASSIGN(m,PyObject_CallFunction(m,"")) return -1;
  r=PyInt_AsLong(m);
  Py_DECREF(m);
  return r;
}

static PyObject *
subclass_item(PyObject *self, int index)
{
  PyObject *m;
  PyExtensionClass *t;

  UNLESS(m=subclass_getspecial(self,py__getitem__)) return NULL;
  if(UnboundCMethod_Check(m) && AsCMethod(m)->meth==getitem_by_name
     && SubclassInstance_Check(self,AsCMethod(m)->type))
    {
      t=(PyExtensionClass*)AsCMethod(m)->type;
      if(t->tp_as_sequence && t->tp_as_sequence->sq_item)
	{
	  Py_DECREF(m);
	  return t->tp_as_sequence->sq_item(self,index);
	}
    }
  if(UnboundEMethod_Check(m))
    ASSIGN(m,PyObject_CallFunction(m,"Oi",self,index));
  else
    ASSIGN(m,PyObject_CallFunction(m,"i",index));
  return m;
}

static PyObject *
subclass_slice(PyObject *self, int i1, int i2)
{
  PyObject *m;

  UNLESS(m=subclass_getspecial(self,py__getslice__)) return NULL;
  if(UnboundCMethod_Check(m) && AsCMethod(m)->meth==slice_by_name
     && SubclassInstance_Check(self,AsCMethod(m)->type))
    ASSIGN(m,AsCMethod(m)->type->tp_as_sequence->sq_slice(self,i1,i2));
  else if(UnboundEMethod_Check(m))
    ASSIGN(m,PyObject_CallFunction(m,"Oii",self,i1,i2));
  else
    ASSIGN(m,PyObject_CallFunction(m,"ii",i1,i2));
  return m;
}

static long
subclass_ass_item(PyObject *self, int index, PyObject *v)
{
  PyObject *m;
  PyExtensionClass *t;

  if(! v && (m=subclass_getspecial(self,py__delitem__)))
    {
      if(UnboundEMethod_Check(m))
	{
	  UNLESS_ASSIGN(m,PyObject_CallFunction(m,"Oi",self,index)) return -1;
	}
      else UNLESS_ASSIGN(m,PyObject_CallFunction(m,"i",index)) return -1;
      Py_DECREF(m);
      return 0;
    }

  UNLESS(m=subclass_getspecial(self,py__setitem__)) return -1;
  if(UnboundCMethod_Check(m) &&
     AsCMethod(m)->meth==(PyCFunction)setitem_by_name
     && SubclassInstance_Check(self,AsCMethod(m)->type))
    {
      t=(PyExtensionClass*)AsCMethod(m)->type;
      if(t->tp_as_sequence && t->tp_as_sequence->sq_ass_item)
	{
	  Py_DECREF(m);
	  return t->tp_as_sequence->sq_ass_item(self,index,v);
	}
    }
  if(! v)
    {
      PyErr_SetObject(PyExc_AttributeError, py__delitem__);
      return -1;
    }
  if(UnboundEMethod_Check(m))
    {
      UNLESS_ASSIGN(m,PyObject_CallFunction(m,"OiO",self,index,v)) return -1;
    }
  else UNLESS_ASSIGN(m,PyObject_CallFunction(m,"iO",index,v)) return -1;
  Py_DECREF(m);
  return 0;
}

static int
subclass_ass_slice(PyObject *self, int i1, int i2, PyObject *v)
{
  PyObject *m;
  long r;

  if(! v && (m=subclass_getspecial(self,py__delslice__)))
    {
      if(UnboundEMethod_Check(m))
	{
	  UNLESS_ASSIGN(m,PyObject_CallFunction(m,"Oii",self,i1,i2)) return -1;
	}
      else UNLESS_ASSIGN(m,PyObject_CallFunction(m,"ii",i1,i2)) return -1;
      Py_DECREF(m);
      return 0;
    }

  UNLESS(m=subclass_getspecial(self,py__setslice__)) return -1;
  if(UnboundCMethod_Check(m) &&
     AsCMethod(m)->meth==(PyCFunction)ass_slice_by_name
     && SubclassInstance_Check(self,AsCMethod(m)->type))
    {	
      r=AsCMethod(m)->type->tp_as_sequence->sq_ass_slice(self,i1,i2,v);
      Py_DECREF(m);
      return r;
    }

  if(! v)
    {
      PyErr_SetObject(PyExc_AttributeError, py__delslice__);
      return -1;
    }

  if(UnboundEMethod_Check(m))
    {
      UNLESS_ASSIGN(m,PyObject_CallFunction(m,"OiiO",self,i1,i2,v))
	return -1;
    }
  else UNLESS_ASSIGN(m,PyObject_CallFunction(m,"iiO",i1,i2,v)) return -1;
  Py_DECREF(m);
  return 0;
}  

static PyObject *
subclass_concat(PyObject *self, PyObject *v)
{
  PyObject *m;

  UNLESS(m=subclass_getspecial(self,py__concat__))
    { /* Maybe we should check for __add__ */
      PyObject *am;

      PyErr_Clear();
      UNLESS(am=subclass_getspecial(self,py__add__)) return NULL;
      if(m=subclass_getspecial(self,py__coerce__))
	{
	  if(UnboundCMethod_Check(m) && AsCMethod(m)->meth==coerce_by_name
	     && SubclassInstance_Check(self,AsCMethod(m)->type))
	    {
	      PyObject *x,*y;

	      x=self;
	      y=v;
	      if(0==AsCMethod(m)->type->tp_as_number->nb_coerce(&x,&y))
		{
		  Py_DECREF(am);
		  if(x->ob_type->tp_as_number)
		    am=x->ob_type->tp_as_number->nb_add(x,y);
		  else
		    am=NULL;
		  Py_DECREF(m);
		  Py_DECREF(x);
		  Py_DECREF(y);
		  if(am) return am;
		}
	    }
	  Py_DECREF(m);
	}
      Py_DECREF(am);
      PyErr_SetString(PyExc_AttributeError,
	 "No __add__ or __concat__ methods, or maybe I'm just being stupid.");
      return NULL;
    }

  if(UnboundCMethod_Check(m) && AsCMethod(m)->meth==concat_by_name
     && SubclassInstance_Check(self,AsCMethod(m)->type))
    ASSIGN(m,AsCMethod(m)->type->tp_as_sequence->sq_concat(self,v));
  else if(UnboundEMethod_Check(m))
    ASSIGN(m,PyObject_CallFunction(m,"OO",self,v));
  else
    ASSIGN(m,PyObject_CallFunction(m,"O",v));
  return m;
}

static PyObject *
subclass_repeat(PyObject *self, int v)
{
  PyObject *m;

  UNLESS(m=subclass_getspecial(self,py__repeat__)) return NULL;
  if(UnboundCMethod_Check(m) && AsCMethod(m)->meth==repeat_by_name
     && SubclassInstance_Check(self,AsCMethod(m)->type))
    ASSIGN(m,AsCMethod(m)->type->tp_as_sequence->sq_repeat(self,v));
  else if(UnboundEMethod_Check(m))
    ASSIGN(m,PyObject_CallFunction(m,"Oi",self,v));
  else
    ASSIGN(m,PyObject_CallFunction(m,"i",v));
  return m;
}

PySequenceMethods subclass_as_sequence = {
	(inquiry)subclass_length,   		/*sq_length*/
	(binaryfunc)subclass_concat,		/*sq_concat*/
	(intargfunc)subclass_repeat,		/*sq_repeat*/
	(intargfunc)subclass_item,		/*sq_item*/
	(intintargfunc)subclass_slice,		/*sq_slice*/
	(intobjargproc)subclass_ass_item,	/*sq_ass_item*/
	(intintobjargproc)subclass_ass_slice,	/*sq_ass_slice*/
};

static PyObject *
subclass_subscript(PyObject *self, PyObject *key)
{
  PyObject *m;
  PyExtensionClass *t;

  UNLESS(m=subclass_getspecial(self,py__getitem__)) return NULL;
  if(UnboundCMethod_Check(m) &&
     AsCMethod(m)->meth==(PyCFunction)getitem_by_name
     && SubclassInstance_Check(self,AsCMethod(m)->type))
    {
      t=(PyExtensionClass*)AsCMethod(m)->type;
      if(t->tp_as_mapping && t->tp_as_mapping->mp_subscript)
	{
	  Py_DECREF(m);
	  return t->tp_as_mapping->mp_subscript(self,key);
	}
    }
  if(UnboundEMethod_Check(m))
    ASSIGN(m,PyObject_CallFunction(m,"OO",self,key));
  else
    ASSIGN(m,PyObject_CallFunction(m,"O",key));
  return m;
}

static long
subclass_ass_subscript(PyObject *self, PyObject *index, PyObject *v)
{
  PyObject *m;
  PyExtensionClass *t;

  if(! v && (m=subclass_getspecial(self,py__delitem__)))
    {
      if(UnboundEMethod_Check(m))
	{
	  UNLESS_ASSIGN(m,PyObject_CallFunction(m,"OO",self,index)) return -1;
	}
      else UNLESS_ASSIGN(m,PyObject_CallFunction(m,"O",index)) return -1;
      Py_DECREF(m);
      return 0;
    }

  UNLESS(m=subclass_getspecial(self,py__setitem__)) return -1;
  if(UnboundCMethod_Check(m) &&
     AsCMethod(m)->meth==(PyCFunction)setitem_by_name
     && SubclassInstance_Check(self,AsCMethod(m)->type))
    {
      t=(PyExtensionClass*)AsCMethod(m)->type;
      if(t->tp_as_sequence && t->tp_as_mapping->mp_ass_subscript)
	{
	  Py_DECREF(m);
	  return t->tp_as_mapping->mp_ass_subscript(self,index,v);
	}
    }
  if(! v)
    {
      PyErr_SetObject(PyExc_AttributeError, py__delitem__);
      return -1;
    }
  if(UnboundEMethod_Check(m))
    {
      UNLESS_ASSIGN(m,PyObject_CallFunction(m,"OOO",self,index,v)) return -1;
    }
  else UNLESS_ASSIGN(m,PyObject_CallFunction(m,"OO",index,v)) return -1;
  Py_DECREF(m);
  return 0;
}

PyMappingMethods subclass_as_mapping = {
	(inquiry)subclass_length,		/*mp_length*/
	(binaryfunc)subclass_subscript,		/*mp_subscript*/
	(objobjargproc)subclass_ass_subscript,	/*mp_ass_subscript*/
};

static int
dealloc_base(PyObject *inst, PyExtensionClass* self)
{
  int i,l;
  PyObject *t;

  l=PyTuple_Size(self->bases);
  for(i=0; i < l; i++)
    {
      t=PyTuple_GET_ITEM(self->bases, i);
      if(ExtensionClass_Check(t))
	{
	  if(AsExtensionClass(t)->bases)
	    {
	      if(dealloc_base(inst,AsExtensionClass(t))) return 1;
	    }
	  else
	    {
	      if(((PyExtensionClass*)t)->tp_dealloc)
		{
		  ((PyExtensionClass*)t)->tp_dealloc(inst);
		  return 1;
		}
	    }
	}
    }
  return 0;
}

static void
subclass_dealloc(PyObject *self)
{
  PyObject *m, *t, *v, *tb;

#ifdef TRACE_DEALLOC
  fprintf(stderr,"Deallocating a %s\n", self->ob_type->tp_name);
#endif

  PyErr_Fetch(&t,&v,&tb);
  Py_INCREF(self);		/* Give us a new lease on life */

  if(m=subclass_getspecial(self,py__del__))
    {
      if(UnboundEMethod_Check(m))
	ASSIGN(m,PyObject_CallFunction(m,"O",self));
      else
	ASSIGN(m,PyObject_CallFunction(m,""));
      Py_XDECREF(m);
    }

  PyErr_Clear();

  if(--self->ob_refcnt > 0)
    {
      PyErr_Restore(t,v,tb);
      return; /* we added a reference; don't delete now */
    }
  
  Py_XDECREF(INSTANCE_DICT(self));
  Py_DECREF(self->ob_type);

  dealloc_base(self,(PyExtensionClass*)self->ob_type);

  PyErr_Restore(t,v,tb);
}

static void
datafull_baseclassesf(PyExtensionClass *type, PyObject **c1, PyObject **c2)
{
  /* Find the number of classes that have data and return them.
     There should be no more than one.
     */
  int l, i, n=0;
  PyObject *base;
  
  l=PyTuple_Size(type->bases);
  for(i=0; i < l && ! (*c1 && *c2); i++)
    {
      base=PyTuple_GET_ITEM(type->bases, i);
      if(ExtensionClass_Check(base))
	{
	  if(AsExtensionClass(base)->bases)
	    datafull_baseclassesf(AsExtensionClass(base),c1,c2);
	  else
	    {
	      if(AsExtensionClass(base)->tp_basicsize >
		 sizeof(PyPureMixinObject) ||
		 AsExtensionClass(base)->tp_itemsize > 0)
		{
		  if(! *c1)
		    *c1=base;
		  else if(*c1 != base)
		    *c2=base;
		}      
	    }
	}
    }
}

static int
datafull_baseclasses(PyExtensionClass *type)
{
  PyObject *c1=0, *c2=0;
  datafull_baseclassesf(type, &c1, &c2);
  if(c2) return 2;
  if(c1) return 1;
  return 0;
}

static PyObject *
datafull_baseclass(PyExtensionClass *type)
{
  /* Find the baseclass that has data and.  There should be only one. */
  int l, i, n=0;
  PyObject *base, *dbase;
  
  l=PyTuple_Size(type->bases);
  for(i=0; i < l; i++)
    {
      base=PyTuple_GET_ITEM(type->bases, i);
      if(ExtensionClass_Check(base))
	{
	  if(AsExtensionClass(base)->bases)
	    {
	      if(dbase=datafull_baseclass(AsExtensionClass(base)))
		return dbase;
	    }
	  else
	    {
	      if(AsExtensionClass(base)->tp_basicsize >
		 sizeof(PyPureMixinObject) ||
		 AsExtensionClass(base)->tp_itemsize > 0)
		return base;
	    }
	}
    }
  return NULL;
}

static PyObject *
extension_baseclass(PyExtensionClass *type)
{
  /* Find the first immediate base class that is an extension class */
  int l, i, n=0;
  PyObject *base;
  
  l=PyTuple_Size(type->bases);
  for(i=0; i < l; i++)
    {
      base=PyTuple_GET_ITEM(type->bases, i);
      if(ExtensionClass_Check(base)) return base;
    }
  return PyErr_Format(PyExc_TypeError,
		      "No extension class found in subclass", NULL);
}

static int 
subclass_hasattr(PyExtensionClass *type, PyObject *name)
{
  PyObject *o;

  if(o=CCL_getattro(type,name))
    {
      Py_DECREF(o);
      return 1;
    }
  PyErr_Clear();
  return 0;
}

static int
has_number_methods(PyExtensionClass *type)
{
  return (subclass_hasattr(type,py__add__) ||
	  subclass_hasattr(type,py__sub__) ||
	  subclass_hasattr(type,py__mul__) ||
	  subclass_hasattr(type,py__div__) ||
	  subclass_hasattr(type,py__mod__) ||
	  subclass_hasattr(type,py__pow__) ||
	  subclass_hasattr(type,py__divmod__) ||
	  subclass_hasattr(type,py__lshift__) ||
	  subclass_hasattr(type,py__rshift__) ||
	  subclass_hasattr(type,py__and__) ||
	  subclass_hasattr(type,py__or__) ||
	  subclass_hasattr(type,py__xor__) ||
	  subclass_hasattr(type,py__coerce__) ||
	  subclass_hasattr(type,py__neg__) ||
	  subclass_hasattr(type,py__pos__) ||
	  subclass_hasattr(type,py__abs__) ||
	  subclass_hasattr(type,py__nonzero__) ||
	  subclass_hasattr(type,py__inv__) ||
	  subclass_hasattr(type,py__int__) ||
	  subclass_hasattr(type,py__long__) ||
	  subclass_hasattr(type,py__float__) ||
	  subclass_hasattr(type,py__oct__) ||
	  subclass_hasattr(type,py__hex__)
	  );
}	  

static int
has_collection_methods(PyExtensionClass *type)
{
  return (subclass_hasattr(type,py__getitem__) ||
	  subclass_hasattr(type,py__setitem__) ||
	  subclass_hasattr(type,py__getslice__) ||
	  subclass_hasattr(type,py__setslice__) ||
	  subclass_hasattr(type,py__concat__) ||
	  subclass_hasattr(type,py__repeat__) ||
	  subclass_hasattr(type,py__len__) 
	  );
}	  

static void
subclass_init_getattr(PyExtensionClass *self, PyObject *methods)
{
  PyObject *m;

  if((m=CCL_getattr(self,py__getattr__,0)))
    {
      if(UnboundCMethod_Check(m) && AsCMethod(m)->meth==getattr_by_name
	 && Subclass_Check(self,AsCMethod(m)->type))
	{
	  self->tp_getattr=AsCMethod(m)->type->tp_getattr;
	}
      else if(UnboundCMethod_Check(m) && AsCMethod(m)->meth==getattro_by_name
	   && Subclass_Check(self,AsCMethod(m)->type))
	  {
	    self->tp_getattro=AsCMethod(m)->type->tp_getattro;
	  }
      else
	{
	  PyObject_SetItem(methods,py__getattr__,m);
	  self->tp_getattro=subclass_getattro;
	}
      Py_DECREF(m);
    }
  else
    {
      PyErr_Clear();
      self->tp_getattro=EC_findiattro;
    }
}

static void
subclass_init_setattr(PyExtensionClass *self, PyObject *methods)
{
  PyObject *m;

  if((m=CCL_getattr(self,py__setattr__,0)))
    {
      if(UnboundCMethod_Check(m) && AsCMethod(m)->meth==setattr_by_name
	 && Subclass_Check(self,AsCMethod(m)->type))
	{
	  self->tp_setattr=AsCMethod(m)->type->tp_setattr;
	}
      else if(UnboundCMethod_Check(m) && AsCMethod(m)->meth==setattro_by_name
	   && Subclass_Check(self,AsCMethod(m)->type))
	  {
	    self->tp_setattro=AsCMethod(m)->type->tp_setattro;
	  }
      else
	{
	  PyObject_SetItem(methods,py__setattr__,m);
	  self->tp_setattro=subclass_setattro;
	}
      Py_DECREF(m);
    }
  else
    {
      PyErr_Clear();
      self->tp_setattro=subclass_simple_setattro;
    }
}

static PyObject *
CopyMethods(PyExtensionClass *type, PyObject *base_methods)
{
  PyObject *methods, *key, *v;
  int pos;

  UNLESS(type->class_dictionary && PyDict_Check(base_methods) &&
	 ExtensionInstance_Check(type->class_dictionary))
    {
      Py_INCREF(base_methods);
      return base_methods;
    }

  UNLESS(methods=
	 PyObject_CallObject((PyObject*)type->class_dictionary->ob_type, NULL))
    return NULL;

  for(pos=0; PyDict_Next(base_methods, &pos, &key, &v); )
    UNLESS(0 <= PyObject_SetItem(methods,key,v)) goto err;

  return methods;

err:
  Py_DECREF(methods);
  return NULL;
}

/* Constructor for building subclasses of C classes.

   That is, we want to build a C class object that described a
   subclass of a built-in type.
 */
static PyObject *
subclass__init__(PyExtensionClass *self, PyObject *args)
{
  PyObject *bases, *methods, *class_init;
  PyExtensionClass *type;
  char *name, *p;
  int dynamic=1, l;

  UNLESS(PyArg_Parse(args,"(sOO)", &name, &bases, &methods)) return NULL;
  l=strlen(name)+1;
  UNLESS(p=(char*)malloc(l*sizeof(char))) return PyErr_NoMemory();
  memcpy(p,name,l);
  name=p;

  UNLESS(PyTuple_Check(bases) && PyTuple_Size(bases))
    {
      PyErr_SetString
	(PyExc_TypeError,
	 "second argument must be a tuple of 1 or more base classes");
    }

  self->bases=bases;
  Py_INCREF(bases);

  if(datafull_baseclasses(self) > 1)
    {
      PyErr_SetString(PyExc_TypeError, "too many datafull base classes");
      return NULL;
    }
  UNLESS(type=(PyExtensionClass *)datafull_baseclass(self))
    UNLESS(type=(PyExtensionClass *)extension_baseclass(self)) return NULL;
    

  self->tp_name=name;

  UNLESS(self->class_dictionary=CopyMethods(type,methods)) return NULL;

#define copy_member(M) self->M=type->M
  copy_member(ob_size);
  copy_member(class_flags);

  if(type->bases)
    copy_member(tp_basicsize);
  else
    {
      self->tp_basicsize=type->tp_basicsize/sizeof(PyObject*)*sizeof(PyObject*);
      if(self->tp_basicsize < type->tp_basicsize)
	self->tp_basicsize += sizeof(PyObject*); /* To align on PyObject */
      self->tp_basicsize += sizeof(PyObject*); /* For instance dictionary */
    }

  copy_member(tp_itemsize);
  copy_member(tp_print);
  self->tp_dealloc=subclass_dealloc;

  subclass_init_getattr(self,methods);
  subclass_init_setattr(self,methods);

#define subclass_set(OP,N) \
  self->tp_ ##OP = subclass_ ##OP
  
  subclass_set(compare,cmp);
  subclass_set(repr,repr);

  if(subclass_hasattr(self,py__of__))
    self->class_flags |= EXTENSIONCLASS_BINDABLE_FLAG;

  if(dynamic || has_number_methods(self))
    {
      self->tp_as_number=(PyNumberMethods*)malloc(sizeof(PyNumberMethods));
      UNLESS(self->tp_as_number) return PyErr_NoMemory();
      *(self->tp_as_number)=subclass_as_number;
    }
  else
    self->tp_as_number=NULL;
    
  if(dynamic || has_collection_methods(self))
    {
      self->tp_as_sequence=
	(PySequenceMethods*)malloc(sizeof(PySequenceMethods));
      UNLESS(self->tp_as_sequence) return PyErr_NoMemory();
      *(self->tp_as_sequence)=subclass_as_sequence;

      self->tp_as_mapping=(PyMappingMethods*)malloc(sizeof(PyMappingMethods));
      UNLESS(self->tp_as_mapping) return PyErr_NoMemory();
      *(self->tp_as_mapping)=subclass_as_mapping;
    }
  else
    {
      self->tp_as_sequence=NULL;
      self->tp_as_sequence=NULL;
    }
  subclass_set(hash,hash);
  subclass_set(call,call);
  subclass_set(str,str);
  self->tp_doc=0;

  /* Check for and use __class_init__ */
  if(class_init=PyObject_GetAttrString(AsPyObject(self),"class__init__"))
    {
      UNLESS_ASSIGN(class_init,PyObject_CallObject(class_init,NULL))
	return NULL;
      Py_DECREF(class_init);
    }
  else
    PyErr_Clear();

  Py_INCREF(Py_None);
  return Py_None;
}

struct PyMethodDef ExtensionClass_methods[] = {
  {"__init__",(PyCFunction)subclass__init__,0,""},
  
  {NULL,		NULL}		/* sentinel */
};

static PyExtensionClass ECType = {
  PyObject_HEAD_INIT(NULL)
  0,				/*ob_size*/
  "ExtensionClass",		/*tp_name*/
  sizeof(PyExtensionClass),    	/*tp_basicsize*/
  0,				/*tp_itemsize*/
  /* methods */
  (destructor)CCL_dealloc,	/*tp_dealloc*/
  (printfunc)0,			/*tp_print*/
  (getattrfunc)0,		/*tp_getattr*/
  (setattrfunc)0,		/*tp_setattr*/
  (cmpfunc)0,			/*tp_compare*/
  (reprfunc)CCL_repr,		/*tp_repr*/
  0,				/*tp_as_number*/
  0,				/*tp_as_sequence*/
  0,				/*tp_as_mapping*/
  (hashfunc)0,			/*tp_hash*/
  (ternaryfunc)CCL_call,       	/*tp_call*/
  (reprfunc)0,			/*tp_str*/
  (getattrofunc)CCL_getattro,	/*tp_getattr with object key*/
  (setattrofunc)CCL_setattro,	/*tp_setattr with object key*/
  /* Space for future expansion */
  0L,0L,
  "C classes", /* Documentation string */
  METHOD_CHAIN(ExtensionClass_methods)
};

/* List of methods defined in the module */

static struct PyMethodDef CC_methods[] = {
  {NULL,		NULL}		/* sentinel */
};

static int
export_type(PyObject *dict, char *name, PyExtensionClass *typ)
{
  initializeBaseExtensionClass(typ);
  return PyMapping_SetItemString(dict,name,(PyObject*)typ);
}

static struct ExtensionClassCAPIstruct
TrueExtensionClassCAPI = {
  export_type,
  EC_findiattrs,
  EC_findiattro,
  subclass_simple_setattr,
  subclass_simple_setattro,
  (PyObject*)&ECType,
  (PyObject*)&PMethodType,
  PMethod_New,
};

void
initExtensionClass()
{
  PyObject *m, *d;
  PURE_MIXIN_CLASS(Base, "Minimalbase class for Extension Classes", NULL);

  PMethodType.ob_type=&PyType_Type;
  CMethodType.ob_type=&PyType_Type;
  ECTypeType.ob_type=&PyType_Type;
  ECType.ob_type=&ECTypeType;
  
  /* Create the module and add the functions */
  m = Py_InitModule4("ExtensionClass", CC_methods,
		     ExtensionClass_module_documentation,
		     (PyObject*)NULL,PYTHON_API_VERSION);

  /* Add some symbolic constants to the module */
  d = PyModule_GetDict(m);

  init_py_names();

  initializeBaseExtensionClass(&ECType);
  PyDict_SetItemString(d, "ExtensionClass", (PyObject*)&ECType);

  initializeBaseExtensionClass(&BaseType);
  PyDict_SetItemString(d, "Base", (PyObject*)&BaseType);

  PyDict_SetItemString(d, "PythonMethodType", (PyObject*)&PMethodType);
  PyDict_SetItemString(d, "ExtensionMethodType", (PyObject*)&CMethodType);

  /* Export C attribute lookup API */
  PyExtensionClassCAPI=&TrueExtensionClassCAPI;
  PyDict_SetItemString(d, "CAPI",
		       PyCObject_FromVoidPtr(PyExtensionClassCAPI,NULL));

  CHECK_FOR_ERRORS("can't initialize module ExtensionClass");
}

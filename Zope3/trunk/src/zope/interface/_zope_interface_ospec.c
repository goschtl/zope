/*****************************************************************************

 Copyright (c) 2003 Zope Corporation and Contributors.
 All Rights Reserved.

 This software is subject to the provisions of the Zope Public License,
 Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
 THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
 WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
 FOR A PARTICULAR PURPOSE.

 *****************************************************************************/
 

#include "Python.h"
#include "structmember.h"

static PyObject *str___provides__, *str___implements__, *str___class__;
static PyObject *str___dict__, *str___signature__;
static PyObject *_implements_reg, *classImplements, *proxySig, *oldSpecSig;

#define TYPE(O) ((PyTypeObject*)(O))
#define OBJECT(O) ((PyObject*)(O))
#define CLASSIC(O) ((PyClassObject*)(O))

typedef struct {
  PyObject_HEAD
  PyObject *__signature__;
} ISB;

static PyMemberDef ISB_members[] = {
  { "__signature__", T_OBJECT_EX, offsetof(ISB, __signature__), 0 },
  {NULL}	/* Sentinel */
};

static char ISBtype__doc__[] = 
"InterfaceSpecification base class that provides a __signature__ slot"
;

static PyTypeObject ISBType = {
	PyObject_HEAD_INIT(NULL)
	/* ob_size           */ 0,
	/* tp_name           */ "zope.interface._zope_interface_ospec."
                                "InterfaceSpecificationBase",
	/* tp_basicsize      */ sizeof(ISB),
	/* tp_itemsize       */ 0,
	/* tp_dealloc        */ (destructor)0,
	/* tp_print          */ (printfunc)0,
	/* tp_getattr        */ (getattrfunc)0,
	/* tp_setattr        */ (setattrfunc)0,
	/* tp_compare        */ (cmpfunc)0,
	/* tp_repr           */ (reprfunc)0,
	/* tp_as_number      */ 0,
	/* tp_as_sequence    */ 0,
	/* tp_as_mapping     */ 0,
	/* tp_hash           */ (hashfunc)0,
	/* tp_call           */ (ternaryfunc)0,
	/* tp_str            */ (reprfunc)0,
        /* tp_getattro       */ (getattrofunc)0,
        /* tp_setattro       */ (setattrofunc)0,
        /* tp_as_buffer      */ 0,
        /* tp_flags          */ Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
	/* tp_doc            */ ISBtype__doc__,
        /* tp_traverse       */ (traverseproc)0,
        /* tp_clear          */ (inquiry)0,
        /* tp_richcompare    */ (richcmpfunc)0,
        /* tp_weaklistoffset */ (long)0,
        /* tp_iter           */ (getiterfunc)0,
        /* tp_iternext       */ (iternextfunc)0,
        /* tp_methods        */ 0,
        /* tp_members        */ ISB_members,
        /* tp_getset         */ 0,
        /* tp_base           */ 0,
        /* tp_dict           */ 0, /* internal use */
        /* tp_descr_get      */ (descrgetfunc)0,
        /* tp_descr_set      */ (descrsetfunc)0,
        /* tp_dictoffset     */ 0,
        /* tp_init           */ (initproc)0,
        /* tp_alloc          */ (allocfunc)0,
        /* tp_new            */ (newfunc)PyType_GenericNew,
};

typedef struct {
  PyObject_HEAD
  PyObject *ob;
} OSpec;

static PyObject *
OSpec_init(OSpec *self, PyObject *args, PyObject *kwds)
{
	static char *kwlist[] = {"ob", NULL};
        PyObject *ob;

        if (! PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, 
                                          &ob))
        	return NULL; 

        Py_INCREF(ob);
        self->ob = ob;

    	Py_INCREF(Py_None);
    	return Py_None;
}

static void
OSpec_dealloc(OSpec *self)
{
  Py_XDECREF(self->ob);
  self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
OSpec_getob(OSpec *self, void *closure)
{
  if (self->ob == NULL) {
    PyErr_SetString(PyExc_AttributeError, "No ob attribute set");
    return NULL;
  }

  Py_INCREF(self->ob);
  return self->ob;
}

static PyObject *
getsig(PyObject *spec, PyObject *cls)
{
  PyObject *sig;

  if (PyObject_TypeCheck(spec, &ISBType))
    {
      sig = ((ISB*)spec)->__signature__;
      if (sig == NULL)
        {
          PyErr_SetString(PyExc_TypeError, 
                          "Specification has no __signature__");
          return NULL;
        }
      Py_INCREF(sig);
    }
  else
    { /* Wrong type of specification */
      if (cls == NULL)
        {

          /* This isn't the right kind of thing. Check for a
             __signature__ anyway. */

          sig = PyObject_GetAttr(spec, str___signature__);
        }
      else
        /* Maybe it's an old style declaration */
        sig = PyObject_CallFunctionObjArgs(oldSpecSig, cls, spec, NULL);
    }

  return sig;
}

static PyObject *
OSpec_getsig(OSpec *self, void *closure)
{
  PyObject *provides, *psig=0, *cls, *key, *dict, *implements, *sig=0, *result;

  if (self->ob == NULL) {
    PyErr_SetString(PyExc_AttributeError, "No ob attribute set");
    return NULL;
  }

  provides = PyObject_GetAttr(self->ob, str___provides__);
  if (provides == NULL)
    PyErr_Clear();
  else 
    {
      psig = getsig(provides, NULL);
      Py_DECREF(provides);
      if (psig == NULL)
        return NULL;
    }

  /* Own: psig */

  /* Whimper. We have to do a getattr, because ob may be a proxy */
  cls = PyObject_GetAttr(self->ob, str___class__);
  if (cls == NULL)
    {
      PyErr_Clear();
      goto done;
    }

  /* Own: psig, cls */

  /* Ultimately, we get the implementation spec from a dict with some
     key, where the dict is normally the class dict and the key is
     normally '__implements__'. */

  key = str___implements__;
  
  if (PyClass_Check(cls))
    {
      dict = CLASSIC(cls)->cl_dict;
      Py_INCREF(dict);
    }
  else if (PyType_Check(cls))
    {
      if (TYPE(cls)->tp_flags & Py_TPFLAGS_HEAPTYPE)
        dict = TYPE(cls)->tp_dict;
      else
        {
          dict = _implements_reg;
          key = cls;
        }
      Py_INCREF(dict);
    }
  else
    dict = PyObject_GetAttr(cls, str___dict__);

  /* Own: psig, cls, dict */

  if (dict == NULL)
    {
      /* We couldn't get a dict. Must be a proxy */
      PyErr_Clear();
      sig = PyObject_CallFunctionObjArgs(proxySig, cls, NULL);
    }
  else
    {
      if (! PyDict_Check(dict))
        {
          PyErr_SetObject(PyExc_TypeError, dict); 
          return NULL;
        }
      implements = PyDict_GetItem(dict, key);
      if (implements == NULL)
        {
          result = PyObject_CallFunctionObjArgs(classImplements, cls, NULL);
          if (result != NULL)
            {
              Py_DECREF(result);
              implements = PyDict_GetItem(dict, key);
              if (implements == NULL)
                PyErr_SetObject(PyExc_KeyError, key); 
            }
        }

      if (implements != NULL)
        sig = getsig(implements, cls);
      
      Py_DECREF(dict);
    }

  Py_DECREF(cls);


  /* Own: psig */


  if (sig == NULL)
    {
      Py_XDECREF(psig);
      return NULL;
    }

 done:
  if (sig == Py_None && psig != NULL)
    {
      /* We have a provided sig, but the class sig was None, so make class
         sig NULL  */
      Py_DECREF(sig);
      sig = NULL;
    }

  if (sig != NULL)
    if (psig != NULL)
      {
        result = PyTuple_New(2);
        if (result == NULL)
          {
            Py_DECREF(psig);
            Py_DECREF(sig);
            return NULL;
          }
        PyTuple_SET_ITEM(result, 0, psig);
        PyTuple_SET_ITEM(result, 1, sig);
        return result;
      }
    else
      return sig;
  else if (psig != NULL)
    return psig;
  else
    {
      Py_INCREF(Py_None);
      return Py_None;
    }
}    

static PyGetSetDef OSpec_getset[] = {
    {"ob", 
     (getter)OSpec_getob, (setter)0,
     "Subject of the object specification",
     NULL},
    {"__signature__", 
     (getter)OSpec_getsig, (setter)0,
     "Specification signature",
     NULL},
    {NULL}  /* Sentinel */
};




static char OSpecType__doc__[] = 
"Base type for object specifications computed via descriptors (no wrappers)"
;

static PyTypeObject OSpecType = {
	PyObject_HEAD_INIT(NULL)
	/* ob_size           */ 0,
	/* tp_name           */ "zope.interface._zope_interface_ospec."
                                "ObjectSpecificationBase",
	/* tp_basicsize      */ sizeof(OSpec),
	/* tp_itemsize       */ 0,
	/* tp_dealloc        */ (destructor)OSpec_dealloc,
	/* tp_print          */ (printfunc)0,
	/* tp_getattr        */ (getattrfunc)0,
	/* tp_setattr        */ (setattrfunc)0,
	/* tp_compare        */ (cmpfunc)0,
	/* tp_repr           */ (reprfunc)0,
	/* tp_as_number      */ 0,
	/* tp_as_sequence    */ 0,
	/* tp_as_mapping     */ 0,
	/* tp_hash           */ (hashfunc)0,
	/* tp_call           */ (ternaryfunc)0,
	/* tp_str            */ (reprfunc)0,
        /* tp_getattro       */ (getattrofunc)0,
        /* tp_setattro       */ (setattrofunc)0,
        /* tp_as_buffer      */ 0,
        /* tp_flags          */ Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
	/* tp_doc            */ OSpecType__doc__,
        /* tp_traverse       */ (traverseproc)0,
        /* tp_clear          */ (inquiry)0,
        /* tp_richcompare    */ (richcmpfunc)0,
        /* tp_weaklistoffset */ (long)0,
        /* tp_iter           */ (getiterfunc)0,
        /* tp_iternext       */ (iternextfunc)0,
        /* tp_methods        */ 0,
        /* tp_members        */ 0,
        /* tp_getset         */ OSpec_getset,
        /* tp_base           */ 0,
        /* tp_dict           */ 0, /* internal use */
        /* tp_descr_get      */ (descrgetfunc)0,
        /* tp_descr_set      */ (descrsetfunc)0,
        /* tp_dictoffset     */ 0,
        /* tp_init           */ (initproc)OSpec_init,
        /* tp_alloc          */ (allocfunc)0,
        /* tp_new            */ (newfunc)PyType_GenericNew,
};

/* List of methods defined in the module */

static struct PyMethodDef module_methods[] = {

	{NULL,	 (PyCFunction)NULL, 0, NULL}		/* sentinel */
};


static char _zope_interface_ospec_module_documentation[] = 
""
;

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
init_zope_interface_ospec(void)
{
  PyObject *module;
  
  str___implements__ = PyString_FromString("__implements__");
  if (str___implements__ == NULL)
    return;
  
  str___provides__ = PyString_FromString("__provides__");
  if (str___provides__ == NULL)
    return;
  
  str___class__ = PyString_FromString("__class__");
  if (str___class__ == NULL)
    return;
  
  str___dict__ = PyString_FromString("__dict__");
  if (str___dict__ == NULL)
    return;
  
  str___signature__ = PyString_FromString("__signature__");
  if (str___signature__ == NULL)
    return;
  
  _implements_reg = PyDict_New();
  if (_implements_reg == NULL)
    return;

  module = PyImport_ImportModule("zope.interface.declarations");
  if (module == NULL) 
    return;

  classImplements = PyObject_GetAttrString(module, "classImplements");
  if (classImplements == NULL)
    return;

  proxySig = PyObject_GetAttrString(module, "proxySig");
  if (proxySig == NULL)
    return;

  oldSpecSig = PyObject_GetAttrString(module, "oldSpecSig");
  if (oldSpecSig == NULL)
    return;

  Py_DECREF(module);
  
  /* Initialize types: */  
  if (PyType_Ready(&ISBType) < 0)
    return;
  if (PyType_Ready(&OSpecType) < 0)
    return;

  /* Create the module and add the functions */
  module = Py_InitModule3("_zope_interface_ospec", module_methods,
                          _zope_interface_ospec_module_documentation);
  
  if (module == NULL)
    return;
  
  /* Add types: */
  if (PyModule_AddObject(module, "InterfaceSpecificationBase", 
                         (PyObject *)&ISBType) < 0)
    return;
  if (PyModule_AddObject(module, "ObjectSpecificationBase", 
                         (PyObject *)&OSpecType) < 0)
    return;
  if (PyModule_AddObject(module, "_implements_reg", _implements_reg) < 0)
    return;
}


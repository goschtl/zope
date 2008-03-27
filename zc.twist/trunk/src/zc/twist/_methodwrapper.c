#include <Python.h>

/* wrapperobject is not in a header.  Also see wrappertype comment. */
typedef struct {
	PyObject_HEAD
	PyWrapperDescrObject *descr;
	PyObject *self;
} wrapperobject;


static PyObject *
module_getSelf(PyObject *self, PyObject *args)
{
  PyObject *wrapper;
  PyObject *result;

  if (!PyArg_ParseTuple(args, "O", &wrapper))
    return NULL;

/*   wrappertype is not in a header. :-(
     if it were, we also could have used PyArg_ParseTuple to do our type
     checking.  This also would raise a TypeError rather than returning
     None, which would be "more Pythonic".

  if (!PyObject_TypeCheck(wrapper, &wrappertype))
    result = Py_None;
  else
*/
    result = (PyObject*)((wrapperobject*)wrapper)->self;
  
  Py_INCREF(result);
  return result;
}

static PyMethodDef MethodWrapperMethods[] = { 
    {"_get_self", module_getSelf, METH_VARARGS, 
    "get im_self of method wrapper.  NO CHECKS!"}, 
    {NULL, NULL, 0, NULL} /* Sentinel */ 
}; 

PyMODINIT_FUNC 
init_methodwrapper(void) 
{ 
    (void) Py_InitModule("_methodwrapper", MethodWrapperMethods); 
} 

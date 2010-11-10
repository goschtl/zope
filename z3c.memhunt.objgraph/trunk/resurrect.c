#include "Python.h"

static PyObject *
Py_conjure (PyObject * self, PyObject * args)
{
  long address;
  if (!PyArg_ParseTuple (args, "l", &address)) {
    return NULL;
  } else {
    PyObject * thing = (PyObject *) address;
    Py_INCREF(thing);
    return thing;
  }
}

/* List of functions defined in the module */

static PyMethodDef resurrect_methods[] = {
  {"conjure",Py_conjure,1},
  {NULL,NULL}/* sentinel */
};

/* Initialization function for the module (*must* be called initresurrect) */

void
initresurrect()
{
  PyObject *m;
  m = Py_InitModule("resurrect", resurrect_methods);
}

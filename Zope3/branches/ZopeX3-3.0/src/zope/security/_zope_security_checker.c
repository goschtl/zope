#include <Python.h>

static PyObject *_checkers, *NoProxy;
static PyObject *Proxy=NULL, *_defaultChecker, *Checker=NULL;



/* def selectChecker(object): */
/*     """Get a checker for the given object */
/*     The appropriate checker is returned or None is returned. If the */
/*     return value is None, then object should not be wrapped in a proxy. */
/*     """ */

static char selectChecker_doc[] = 
"Get a checker for the given object\n"
"\n"
"The appropriate checker is returned or None is returned. If the\n"
"return value is None, then object should not be wrapped in a proxy.\n"
;

static PyObject *
selectChecker(PyObject *ignored, PyObject *object)
{
  PyObject *checker;

  /* Import names from checker is hasn't been done before */
  if (_defaultChecker == NULL)
    {
      checker = PyImport_ImportModule("zope.security.checker");
      if (checker == NULL)
        return NULL;

      Proxy = PyObject_GetAttrString(checker, "Proxy");
      if (Proxy == NULL)
        return NULL;

      Checker = PyObject_GetAttrString(checker, "Checker");
      if (Checker == NULL)
        return NULL;

      _defaultChecker = PyObject_GetAttrString(checker, "_defaultChecker");
      if (_defaultChecker == NULL)
        return NULL;

      Py_DECREF(checker);
    }

/*     checker = _getChecker(type(object), _defaultChecker) */

  checker = PyDict_GetItem(_checkers, (PyObject*)(object->ob_type));
  if (checker == NULL)
    checker = _defaultChecker;

/*     if checker is NoProxy: */
/*         return None */

  if (checker == NoProxy)
    {
      Py_INCREF(Py_None);
      return Py_None;
    }

/*     if checker is _defaultChecker and isinstance(object, Exception): */
/*         return None */

  if (checker == _defaultChecker 
      && PyObject_IsInstance(object, PyExc_Exception))
    {
      Py_INCREF(Py_None);
      return Py_None;
    }

/*     while not isinstance(checker, Checker): */
/*         checker = checker(object) */
/*         if checker is NoProxy or checker is None: */
/*             return None */

  Py_INCREF(checker);
  while (! PyObject_TypeCheck(checker, (PyTypeObject*)Checker))
    {
      PyObject *newchecker;
      newchecker = PyObject_CallFunctionObjArgs(checker, object, NULL);
      Py_DECREF(checker);
      if (newchecker == NULL)
        return NULL;
      checker = newchecker;
      if (checker == NoProxy || checker == Py_None)
        {
          Py_DECREF(checker);
          Py_INCREF(Py_None);
          return Py_None;
        }
    }

/*     return checker */

  return checker;
}


static PyMethodDef module_methods[] = {
  {"selectChecker", (PyCFunction)selectChecker, METH_O, selectChecker_doc},
  {NULL}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
init_zope_security_checker(void) 
{
    PyObject* m;

    if ((_checkers = PyDict_New()) == NULL) return;
    NoProxy = PyObject_CallObject((PyObject*)&PyBaseObject_Type, NULL);
    if (NoProxy == NULL)
      return;

    m = Py_InitModule3("_zope_security_checker", module_methods,
                       "C optimizations for zope.security.checker");

    if (m == NULL)
      return;

    Py_INCREF(_checkers);
    PyModule_AddObject(m, "_checkers", _checkers);
    Py_INCREF(NoProxy);
    PyModule_AddObject(m, "NoProxy", NoProxy);
}

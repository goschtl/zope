#include <Python.h>
#include "modsupport.h"
#include "zope/proxy/proxy.h"
#define WRAPPER_MODULE
#include "zope/proxy/context/wrapper.h"

#define Wrapper_Check(wrapper)   (PyObject_TypeCheck(wrapper, &WrapperType))

#define Wrapper_GetObject(wrapper) Proxy_GET_OBJECT((wrapper))

#define Wrapper_GetContext(wrapper) \
        (((WrapperObject *)wrapper)->wrap_context)

#define Wrapper_GetDict(wrapper) \
        (((WrapperObject *)wrapper)->wrap_dict)


static PyTypeObject WrapperType;

static PyObject *
empty_tuple = NULL;

/* Helper for wrap_new/wrap_init; return the base class args tuple
 * from the incoming args tuple.  Returns a new reference.
 */
static PyObject *
create_proxy_args(PyObject *args, PyObject *object)
{
    if (PyTuple_GET_SIZE(args) == 1)
        Py_INCREF(args);
    else {
        args = PyTuple_New(1);
        if (args != NULL) {
            Py_INCREF(object);
            PyTuple_SET_ITEM(args, 0, object);
        }
    }
    return args;
}

/*
 *   Slot methods.
 */

static PyObject *
wrap_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result = NULL;
    PyObject *context;
    PyObject *object;

    if (PyArg_UnpackTuple(args, "__new__", 1, 2, &object, &context)) {
        PyObject *proxyargs = create_proxy_args(args, object);
        if (proxyargs == NULL)
            goto finally;
        result = ProxyType->tp_new(type, proxyargs, NULL);
        Py_DECREF(proxyargs);
    }
 finally:
    return result;
}

static int
wrap_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    int result = -1;
    PyObject *context = NULL;
    PyObject *proxyargs = NULL;
    PyObject *object;

    if (PyArg_UnpackTuple(args, "__init__", 1, 2, &object, &context)) {
        PyObject *temp;
	WrapperObject *wrapper = (WrapperObject *)self;
        proxyargs = create_proxy_args(args, object);
        if (proxyargs == NULL)
            goto finally;
        if (ProxyType->tp_init(self, proxyargs, NULL) < 0)
            goto finally;
        if (wrapper->wrap_context != context) {
            /* XXX This might be a little weird: if a subclass initializes
             * XXX wrap_context, we end up overwriting it, and clearing
             * XXX it if this __init__ is only called with one arg.
             */
            temp = wrapper->wrap_context;
            Py_XINCREF(context);
            wrapper->wrap_context = context;
            Py_XDECREF(temp);
        }
        if (kwds != NULL && PyDict_Size(kwds) > 0) {
            if (wrapper->wrap_dict == NULL) {
                wrapper->wrap_dict = PyDict_Copy(kwds);
                if (wrapper->wrap_dict == NULL) {
                    Py_DECREF(wrapper);
                    goto finally;
                }
            }
            else if (PyDict_Merge(wrapper->wrap_dict, kwds, 1) < 0) {
                Py_DECREF(wrapper);
                goto finally;
            }
        }
        result = 0;
    }
 finally:
    Py_XDECREF(proxyargs);
    return result;
}

static int
wrap_traverse(PyObject *self, visitproc visit, void *arg)
{
    int err = visit(Wrapper_GetObject(self), arg);

    if (!err && Wrapper_GetContext(self) != NULL)
        err = visit(Wrapper_GetContext(self), arg);
    if (!err && Wrapper_GetDict(self) != NULL)
        err = visit(Wrapper_GetDict(self), arg);
    return err;
}

static int
wrap_clear(PyObject *self)
{
    WrapperObject *wrapper = (WrapperObject *)self;
    PyObject *temp;

    if ((temp = wrapper->wrap_dict) != NULL) {
        wrapper->wrap_dict = NULL;
        Py_DECREF(temp);
    }
    if ((temp = wrapper->wrap_context) != NULL) {
        wrapper->wrap_context = NULL;
        Py_DECREF(temp);
    }
    if ((temp = Proxy_GET_OBJECT(wrapper)) != NULL) {
        wrapper->proxy_object = NULL;
        Py_DECREF(temp);
    }
    return 0;
}

static void
wrap_dealloc(PyObject *self)
{
    (void) wrap_clear(self);
    self->ob_type->tp_free(self);
}

/*
 *   Normal methods
 */

static char
reduce__doc__[] =
"__reduce__()\n"
"Raise an exception; this prevents wrappers from being picklable by\n"
"default, even if the underlying object is picklable.";

static PyObject *
wrap_reduce(PyObject *self)
{
    PyObject *pickle_error = NULL;
    PyObject *pickle = PyImport_ImportModule("pickle");

    if (pickle == NULL)
        PyErr_Clear();
    else {
        pickle_error = PyObject_GetAttrString(pickle, "PicklingError");
        if (pickle_error == NULL)
            PyErr_Clear();
    }
    if (pickle_error == NULL) {
        pickle_error = PyExc_RuntimeError;
        Py_INCREF(pickle_error);
    }
    PyErr_SetString(pickle_error,
                    "Wrapper instances cannot be pickled.");
    Py_DECREF(pickle_error);
    return NULL;
}

static PyMethodDef
wrap_methods[] = {
    {"__reduce__", (PyCFunction)wrap_reduce, METH_NOARGS, reduce__doc__},
    {NULL, NULL},
};

statichere PyTypeObject
WrapperType = {
    PyObject_HEAD_INIT(NULL)
    0,
    "wrapper.Wrapper",
    sizeof(WrapperObject),
    0,
    wrap_dealloc,			/* tp_dealloc */
    0,					/* tp_print */
    0,					/* tp_getattr */
    0,					/* tp_setattr */
    0,					/* tp_compare */
    0,					/* tp_repr */
    0,					/* tp_as_number */
    0,					/* tp_as_sequence */
    0,					/* tp_as_mapping */
    0,					/* tp_hash */
    0,					/* tp_call */
    0,					/* tp_str */
    0,					/* tp_getattro */
    0,					/* tp_setattro */
    0,					/* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC
        | Py_TPFLAGS_BASETYPE,		/* tp_flags */
    0,					/* tp_doc */
    wrap_traverse,			/* tp_traverse */
    wrap_clear,				/* tp_clear */
    0,					/* tp_richcompare */
    0,					/* tp_weaklistoffset */
    0,					/* tp_iter */
    0,					/* tp_iternext */
    wrap_methods,			/* tp_methods */
    0,					/* tp_members */
    0,					/* tp_getset */
    0,					/* tp_base */
    0,					/* tp_dict */
    0,					/* tp_descr_get */
    0,					/* tp_descr_set */
    0,					/* tp_dictoffset */
    wrap_init,				/* tp_init */
    0, /*PyType_GenericAlloc,*/		/* tp_alloc */
    wrap_new,				/* tp_new */
    0, /*_PyObject_GC_Del,*/		/* tp_free */
};


static PyObject *
create_wrapper(PyObject *object, PyObject *context)
{
    PyObject *result = NULL;
    PyObject *args;

    if (context == Py_None)
        context = NULL;
    args = PyTuple_New(context ? 2 : 1);
    if (args != NULL) {
        if (context != NULL) {
            PyTuple_SET_ITEM(args, 1, context);
            Py_INCREF(context);
        }
        PyTuple_SET_ITEM(args, 0, object);
        Py_INCREF(object);
        result = PyObject_CallObject((PyObject *)&WrapperType, args);
        Py_DECREF(args);
    }
    return result;
}


static int
api_check(PyObject *obj)
{
    return obj ? Wrapper_Check(obj) : 0;
}

static PyObject *
api_create(PyObject *object, PyObject *context)
{
    if (object == NULL) {
        PyErr_SetString(PyExc_ValueError,
                        "cannot create wrapper around NULL");
        return NULL;
    }
    return create_wrapper(object, context);
}

static PyObject *
missing_wrapper(const char *funcname)
{
    PyErr_Format(PyExc_RuntimeError,
                 "cannot pass NULL to WrapperAPI.%s()", funcname);
    return NULL;
}

static int
check_wrapper(PyObject *wrapper, const char *funcname)
{
    if (wrapper == NULL) {
        (void) missing_wrapper(funcname);
        return 0;
    }
    if (!Wrapper_Check(wrapper)) {
        PyErr_Format(PyExc_TypeError, "%s expected wrapper type; got %s",
                     funcname, wrapper->ob_type->tp_name);
        return 0;
    }
    return 1;
}

static PyObject *
api_getobject(PyObject *wrapper)
{
    if (wrapper == NULL)
        return missing_wrapper("getobject");
    if (Wrapper_Check(wrapper))
        return Wrapper_GetObject(wrapper);
    else
        return wrapper;
}

static PyObject *
api_getbaseobject(PyObject *obj)
{
    if (obj == NULL)
        return missing_wrapper("getbaseobject");
    while (Wrapper_Check(obj)) {
        obj = Wrapper_GetObject(obj);
    }
    return obj;
}

static PyObject *
api_getcontext(PyObject *wrapper)
{
    if (wrapper == NULL)
        return missing_wrapper("getcontext");
    if (Wrapper_Check(wrapper))
        return Wrapper_GetContext(wrapper);
    else
        return NULL;
}

static PyObject *
api_getinnercontext(PyObject *obj)
{
    if (obj == NULL)
        return missing_wrapper("getinnercontext");
    if (Wrapper_Check(obj)) {
        PyObject *wrapper = obj;
        obj = Wrapper_GetObject(wrapper);
        while (Wrapper_Check(obj)) {
            wrapper = obj;
            obj = Wrapper_GetObject(wrapper);
        }
        return Wrapper_GetContext(wrapper);
    }
    else
        return NULL;
}

static PyObject *
api_getinnerwrapper(PyObject *obj)
{
    PyObject *temp;
    if (obj == NULL)
        return missing_wrapper("getinnercontext");
    if (Wrapper_Check(obj)) {
        temp = Wrapper_GetObject(obj);
        while (Wrapper_Check(temp)) {
            obj = temp;
            temp = Wrapper_GetObject(obj);
        }
    }
    else
        return NULL;
    return obj;
}

static PyObject *
api_getdict(PyObject *wrapper)
{
    if (wrapper == NULL)
        return missing_wrapper("getdict");
    if (Wrapper_Check(wrapper))
        return Wrapper_GetDict(wrapper);
    else
        return NULL;
}

static PyObject *
api_getdictcreate(PyObject *wrapper)
{
    PyObject *dict = NULL;

    if (check_wrapper(wrapper, "getdictcreate")) {
        dict = Wrapper_GetDict(wrapper);
        if (dict == NULL) {
            dict = PyDict_New();
            ((WrapperObject *)wrapper)->wrap_dict = dict;
        }
    }
    return dict;
}

static int
api_setobject(PyObject *wrapper, PyObject *object)
{
    WrapperObject *wrap;
    PyObject *oldobject;
    if (wrapper == NULL || object == NULL) {
        PyErr_SetString(PyExc_RuntimeError,
                        "cannot pass NULL to setobject()");
        return 0;
    }
    if (!check_wrapper(wrapper, "setobject"))
        return 0;
    wrap = (WrapperObject *) wrapper;
    oldobject = Wrapper_GetObject(wrap);
    Py_INCREF(object);
    wrap->proxy_object = object;
    Py_DECREF(oldobject);
    return 1;
}

static int
api_setcontext(PyObject *wrapper, PyObject *context)
{
    WrapperObject *wrap;
    PyObject *oldcontext;
    if (!check_wrapper(wrapper, "setcontext"))
        return 0;
    if (context == Py_None)
        context = NULL;
    wrap = (WrapperObject *) wrapper;
    oldcontext = wrap->wrap_context;
    Py_XINCREF(context);
    wrap->wrap_context = context;
    Py_XDECREF(oldcontext);
    return 1;
}

static WrapperInterface
wrapper_capi = {
    api_check,
    api_create,
    api_getobject,
    api_getbaseobject,
    api_getcontext,
    api_getinnercontext,
    api_getinnerwrapper,
    api_getdict,
    api_getdictcreate,
    api_setobject,
    api_setcontext
};

static char
getobject__doc__[] =
"getobject(wrapper) --> object\n"
"\n"
"Return the underlying object for wrapper, or the passed-in object if\n"
"it is not a wrapper.";

static PyObject *
wrapper_getobject(PyObject *unused, PyObject *obj)
{
    PyObject *result = NULL;

    if (Wrapper_Check(obj))
        result = Wrapper_GetObject(obj);
    else
        result = obj;
    Py_INCREF(result);
    return result;
}

static char
getbaseobject__doc__[] =
"getbaseobject(wrapper) --> object\n"
"\n"
"Return the underlying object for the innermost wrapper in a chain of\n"
"wrappers with 'wrapper' at the head.  Returns None if 'wrapper' isn't a\n"
"wrapper at all.";

static PyObject *
wrapper_getbaseobject(PyObject *unused, PyObject *obj)
{
    obj = api_getbaseobject(obj);
    if (obj == NULL)
        obj = Py_None;
    Py_INCREF(obj);
    return obj;
}

static char
getcontext__doc__[] =
"getcontext(wrapper) --> object | None\n"
"\n"
"Return the context object for wrapper, or None if there isn't one.";

static PyObject *
wrapper_getcontext(PyObject *unused, PyObject *obj)
{
    PyObject *result = NULL;

    if (Wrapper_Check(obj)) {
        result = ((WrapperObject *)obj)->wrap_context;
        if (result == NULL)
            result = Py_None;
    }
    else {
        result = Py_None;
    }
    Py_XINCREF(result);
    return result;
}

static char
getinnercontext__doc__[] =
"getinnercontext(wrapper) --> object | None\n"
"\n"
"Return the context object for the innermost wrapper in a chain of wrappers\n"
"with 'wrapper' at the head, or None if there isn't one.  Returns None if\n"
"'wrapper' isn't a wrapper at all.";

static PyObject *
wrapper_getinnercontext(PyObject *unused, PyObject *obj)
{
    PyObject *result = api_getinnercontext(obj);
    if (result == NULL)
        result = Py_None;
    Py_INCREF(result);
    return result;
}

static char
getinnerwrapper__doc__[] =
"getinnerwrapper(wrapper) --> object | None\n"
"\n"
"Return the innermost wrapper in a chain of wrappers with 'wrapper' at the\n"
"head, or None if there isn't one.  Returns None if 'wrapper' isn't a\n"
"wrapper at all.";

static PyObject *
wrapper_getinnerwrapper(PyObject *unused, PyObject *obj)
{
    PyObject *result = api_getinnerwrapper(obj);
    if (result == NULL)
        result = obj;
    Py_INCREF(result);
    return result;
}

static char
getdict__doc__[] =
"getdict(wrapper) -> dict or None\n"
"\n"
"Return the context dictionary for wrapper, or None if it does not exist.\n";

static PyObject *
wrapper_getdict(PyObject *unused, PyObject *obj)
{
    PyObject *result = NULL;

    if (Wrapper_Check(obj)) {
        result = ((WrapperObject *)obj)->wrap_dict;
        if (result == NULL)
            result = Py_None;
    }
    else
        result = Py_None;
    Py_INCREF(result);
    return result;
}

static char
getdictcreate__doc__[] =
"getdictcreate(wrapper) -> dict\n"
"\n"
"Return the context dictionary for wrapper, creating it if is does not\n"
"exist.";

static PyObject *
wrapper_getdictcreate(PyObject *unused, PyObject *obj)
{
    PyObject *result = NULL;

    if (check_wrapper(obj, "getdictcreate")) {
        result = ((WrapperObject *)obj)->wrap_dict;
        if (result == NULL) {
            result = PyDict_New();
            ((WrapperObject *)obj)->wrap_dict = result;
        }
        Py_XINCREF(result);
    }
    return result;
}

static char
setobject__doc__[] =
"setobject(wrapper, object)\n"
"\n"
"Replaced the wrapped object with object.";

static PyObject *
wrapper_setobject(PyObject *unused, PyObject *args)
{
    PyObject *wrapper;
    PyObject *object;
    PyObject *result = NULL;

    if (PyArg_UnpackTuple(args, "setobject", 2, 2, &wrapper, &object)) {
        if (api_setobject(wrapper, object)) {
            result = Py_None;
            Py_INCREF(result);
        }
    }
    return result;
}

static char
setcontext__doc__[] =
"setcontext(wrapper, context)\n"
"\n"
"Replace the context object for wrapper with context.";

static PyObject *
wrapper_setcontext(PyObject *unused, PyObject *args)
{
    PyObject *wrapper;
    PyObject *context = NULL;
    PyObject *result = NULL;

    if (PyArg_UnpackTuple(args, "setcontext", 1, 2, &wrapper, &context)) {
        if (api_setcontext(wrapper, context)) {
            result = Py_None;
            Py_INCREF(result);
        }
    }
    return result;
}

static PyMethodDef
module_functions[] = {
    {"getobject",       wrapper_getobject,       METH_O,
     getobject__doc__},
    {"getbaseobject",   wrapper_getbaseobject,   METH_O,
     getbaseobject__doc__},
    {"getcontext",      wrapper_getcontext,      METH_O,
     getcontext__doc__},
    {"getinnercontext", wrapper_getinnercontext, METH_O,
     getinnercontext__doc__},
    {"getinnerwrapper", wrapper_getinnerwrapper, METH_O,
     getinnerwrapper__doc__},
    {"getdict",         wrapper_getdict,         METH_O,
     getdict__doc__},
    {"getdictcreate",   wrapper_getdictcreate,   METH_O,
     getdictcreate__doc__},
    {"setobject",       wrapper_setobject,       METH_VARARGS,
     setobject__doc__},
    {"setcontext",      wrapper_setcontext,      METH_VARARGS,
     setcontext__doc__},
    {NULL, NULL, 0, NULL}
};

static char
module___doc__[] =
"Association between an object, a context object, and a dictionary.\n\
\n\
The context object and dictionary give additional context information\n\
associated with a reference to the basic object.  The wrapper objects\n\
act as proxies for the original object.";

static PyObject *
api_object = NULL;


void
initwrapper(void)
{
    PyObject *m;

    if (Proxy_Import() < 0)
        return;

    m = Py_InitModule3("wrapper", module_functions, module___doc__);
    if (m == NULL)
        return;

    WrapperType.ob_type = &PyType_Type;
    WrapperType.tp_base = ProxyType;
    WrapperType.tp_alloc = PyType_GenericAlloc;
    WrapperType.tp_free = _PyObject_GC_Del;
    if (PyType_Ready(&WrapperType) < 0)
        return;

    Py_INCREF(&WrapperType);
    PyModule_AddObject(m, "Wrapper", (PyObject *)&WrapperType);

    if (api_object == NULL) {
        api_object = PyCObject_FromVoidPtr(&wrapper_capi, NULL);
        if (api_object == NULL)
            return;
    }
    Py_INCREF(api_object);
    PyModule_AddObject(m, "_CAPI", api_object);

    if (empty_tuple == NULL)
        empty_tuple = PyTuple_New(0);
}

#include <Python.h>
#include "structmember.h"
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
static PyTypeObject ContextAwareType;

static PyObject *
empty_tuple = NULL;

/* ContextAware type
 *
 * This is a 'marker' type with no methods or members.
 * It is used to mark types that should have all of their binding descriptors
 * rebound to have the self argument be the wrapper instead.
 */

typedef struct {
    PyObject_HEAD
} ContextAwareObject;

statichere PyTypeObject
ContextAwareType = {
    PyObject_HEAD_INIT(NULL)
    0,
    "wrapper.ContextAware",
    sizeof(ContextAwareObject),
    0,
    0,						/* tp_dealloc */
    0,						/* tp_print */
    0,						/* tp_getattr */
    0,						/* tp_setattr */
    0,						/* tp_compare */
    0,						/* tp_repr */
    0,						/* tp_as_number */
    0,						/* tp_as_sequence */
    0,						/* tp_as_mapping */
    0,						/* tp_hash */
    0,						/* tp_call */
    0,						/* tp_str */
    0,						/* tp_getattro */
    0,						/* tp_setattro */
    0,						/* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,	/* tp_flags */
    "ContextAware marker class",		/* tp_doc */
    0,						/* tp_traverse */
    0,						/* tp_clear */
    0,						/* tp_richcompare */
    0,						/* tp_weaklistoffset */
    0,						/* tp_iter */
    0,						/* tp_iternext */
    0,						/* tp_methods */
    0,						/* tp_members */
    0,						/* tp_getset */
    0,						/* tp_base */
    0,						/* tp_dict */
    0,						/* tp_descr_get */
    0,						/* tp_descr_set */
    0,						/* tp_dictoffset */
    0,						/* tp_init */
    0,						/* tp_alloc */
    PyType_GenericNew,				/* tp_new */
    0,						/* tp_free */
};

/* End of ContextAware. */

/* ContextDescriptor type
 *
 * This is a 'marker' type with no methods or members. It is the base type
 * for ContextMethod and ContextProperty, and any other Context-descriptors
 * that are defined in Python.
 */

typedef struct {
    PyObject_HEAD
} ContextDescriptorObject;

statichere PyTypeObject
ContextDescriptorType = {
    PyObject_HEAD_INIT(NULL)
    0,
    "wrapper.ContextDescriptor",
    sizeof(ContextDescriptorObject),
    0,
    0,						/* tp_dealloc */
    0,						/* tp_print */
    0,						/* tp_getattr */
    0,						/* tp_setattr */
    0,						/* tp_compare */
    0,						/* tp_repr */
    0,						/* tp_as_number */
    0,						/* tp_as_sequence */
    0,						/* tp_as_mapping */
    0,						/* tp_hash */
    0,						/* tp_call */
    0,						/* tp_str */
    0,						/* tp_getattro */
    0,						/* tp_setattro */
    0,						/* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,	/* tp_flags */
    "ContextDescriptor base class",		/* tp_doc */
    0,						/* tp_traverse */
    0,						/* tp_clear */
    0,						/* tp_richcompare */
    0,						/* tp_weaklistoffset */
    0,						/* tp_iter */
    0,						/* tp_iternext */
    0,						/* tp_methods */
    0,						/* tp_members */
    0,						/* tp_getset */
    0,						/* tp_base */
    0,						/* tp_dict */
    0,						/* tp_descr_get */
    0,						/* tp_descr_set */
    0,						/* tp_dictoffset */
    0,						/* tp_init */
    0,						/* tp_alloc */
    PyType_GenericNew,				/* tp_new */
    0,						/* tp_free */
};

/* End of ContextDescriptor. */

/* ContextProperty
 * This works exactly like a standard python property, except that it
 * derives from ContextDescriptor.
 */

typedef struct {
    ContextDescriptorObject contextdescriptor;
    PyObject *prop_get;
    PyObject *prop_set;
    PyObject *prop_del;
    PyObject *prop_doc;
} propertyobject;

static char ContextProperty_doc[] =
"ContextProperty(fget, fset, fdel, doc) -> property\n";

static PyMemberDef property_members[] = {
    {"fget", T_OBJECT, offsetof(propertyobject, prop_get), READONLY},
    {"fset", T_OBJECT, offsetof(propertyobject, prop_set), READONLY},
    {"fdel", T_OBJECT, offsetof(propertyobject, prop_del), READONLY},
    {"__doc__",  T_OBJECT, offsetof(propertyobject, prop_doc), READONLY},
    {0}
};

static void
property_dealloc(PyObject *self)
{
    propertyobject *gs = (propertyobject *)self;

    _PyObject_GC_UNTRACK(self);
    Py_XDECREF(gs->prop_get);
    Py_XDECREF(gs->prop_set);
    Py_XDECREF(gs->prop_del);
    Py_XDECREF(gs->prop_doc);
    ContextDescriptorType.tp_dealloc(self);
}

static PyObject *
property_descr_get(PyObject *self, PyObject *obj, PyObject *type)
{
    propertyobject *gs = (propertyobject *)self;

    if (obj == NULL || obj == Py_None) {
        Py_INCREF(self);
        return self;
    }
    if (gs->prop_get == NULL) {
        PyErr_SetString(PyExc_AttributeError, "unreadable attribute");
        return NULL;
    }
    return PyObject_CallFunction(gs->prop_get, "(O)", obj);
}

static int
property_descr_set(PyObject *self, PyObject *obj, PyObject *value)
{
    propertyobject *gs = (propertyobject *)self;
    PyObject *func, *res;

    if (value == NULL)
        func = gs->prop_del;
    else
        func = gs->prop_set;
    if (func == NULL) {
        PyErr_SetString(PyExc_AttributeError,
                        value == NULL ?
                        "can't delete attribute" :
                        "can't set attribute");
        return -1;
    }
    if (value == NULL)
        res = PyObject_CallFunction(func, "(O)", obj);
    else
        res = PyObject_CallFunction(func, "(OO)", obj, value);
    if (res == NULL)
        return -1;
    Py_DECREF(res);
    return 0;
}

static int
property_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *get = NULL, *set = NULL, *del = NULL, *doc = NULL;
    static char *kwlist[] = {"fget", "fset", "fdel", "doc", 0};
    propertyobject *gs = (propertyobject *)self;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|OOOO:property",
                                     kwlist, &get, &set, &del, &doc))
        return -1;

    if (get == Py_None)
        get = NULL;
    if (set == Py_None)
        set = NULL;
    if (del == Py_None)
        del = NULL;

    Py_XINCREF(get);
    Py_XINCREF(set);
    Py_XINCREF(del);
    Py_XINCREF(doc);

    gs->prop_get = get;
    gs->prop_set = set;
    gs->prop_del = del;
    gs->prop_doc = doc;

    return 0;
}

static int
property_traverse(PyObject *self, visitproc visit, void *arg)
{
    propertyobject *pp = (propertyobject *)self;
    int err;

#define VISIT(SLOT) \
    if (pp->SLOT) { \
        err = visit((PyObject *)(pp->SLOT), arg); \
        if (err) \
            return err; \
    }

    VISIT(prop_get);
    VISIT(prop_set);
    VISIT(prop_del);

    return 0;
#undef VISIT
}

PyTypeObject ContextProperty_Type = {
	PyObject_HEAD_INIT(NULL)
	0,						/* ob_size */
	"ContextProperty",				/* tp_name */
	sizeof(propertyobject),				/* tp_basicsize */
	0,						/* tp_itemsize */
	/* methods */
	property_dealloc,		 		/* tp_dealloc */
	0,						/* tp_print */
	0,						/* tp_getattr */
	0,						/* tp_setattr */
	0,						/* tp_compare */
	0,						/* tp_repr */
	0,						/* tp_as_number */
	0,						/* tp_as_sequence */
	0,		       				/* tp_as_mapping */
	0,						/* tp_hash */
	0,						/* tp_call */
	0,						/* tp_str */
	PyObject_GenericGetAttr,			/* tp_getattro */
	0,						/* tp_setattro */
	0,						/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC |
		Py_TPFLAGS_BASETYPE,			/* tp_flags */
	ContextProperty_doc,				/* tp_doc */
	property_traverse,				/* tp_traverse */
	0,						/* tp_clear */
	0,						/* tp_richcompare */
	0,						/* tp_weaklistoffset */
	0,						/* tp_iter */
	0,						/* tp_iternext */
	0,						/* tp_methods */
	property_members,				/* tp_members */
	0,						/* tp_getset */
	0,						/* tp_base */
	0,						/* tp_dict */
	property_descr_get,				/* tp_descr_get */
	property_descr_set,				/* tp_descr_set */
	0,						/* tp_dictoffset */
	property_init,					/* tp_init */
	PyType_GenericAlloc,				/* tp_alloc */
	PyType_GenericNew,				/* tp_new */
	_PyObject_Del,               			/* tp_free */
};

/* end of ContextProperty */


/* ContextMethod
 *
 * A ContextMethod is just like a standard Instance Method descriptor,
 * except that it derives from ContextDescriptor.
 *
 * One difference between a ContextMethod and an class method or static
 * method is that you can get the ContextMethod descriptor from the class
 * using only Python with something like aContextMethod.__get__(None, cls).
 * This is how property descriptors behave.
 * It is not possible to get at a classmethod or staticmethod like that
 * for obvious reasons.
 *
 * This code was mostly copied from instancemethod and classmethod from
 * Python 2.2.2.
 */

typedef struct {
    ContextDescriptorObject contextdescriptor;
    PyObject *cm_callable;
} ContextMethod;

static void
cm_dealloc(PyObject *self)
{
    ContextMethod *cm = (ContextMethod *)self;
    Py_XDECREF(cm->cm_callable);
    ContextDescriptorType.tp_dealloc(self);
}

static PyObject *
cm_descr_get(PyObject *self, PyObject *obj, PyObject *type)
{
    ContextMethod *cm = (ContextMethod *)self;

    if (cm->cm_callable == NULL) {
        PyErr_SetString(PyExc_RuntimeError,
                        "uninitialized ContextMethod object");
        return NULL;
    }
    if (obj == NULL || obj == Py_None) {
        /* obj = NULL;
         * The 'purer' way to do this is to just pass on the
         * call to the type, with a NULL obj.
         * However, we'd like to be able to get the type of this
         * descriptor easily from Python.
         */
        Py_INCREF(self);
        return self;
    }
    return PyMethod_New(cm->cm_callable, obj, type);
}

static int
cm_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    ContextMethod *cm = (ContextMethod *)self;
    PyObject *callable;

    if (!PyArg_ParseTuple(args, "O:callable", &callable))
        return -1;
    Py_INCREF(callable);
    cm->cm_callable = callable;
    return 0;
}

static char ContextMethod_doc[] =
"ContextMethod(function) -> method\n"
"\n"
"Convert a function to be a Context method.\n"
"\n"
"A Context method receives the context wrapper as implicit first argument,\n"
"when this is available from a wrapper, just like an instance method\n"
"receives the instance.\n"
"To declare a Context method, use this idiom:\n"
"\n"
"  class C:\n"
"      def f(self, arg1, arg2, ...): ...\n"
"      f = ContextMethod(f)\n"
"\n";

PyTypeObject ContextMethod_Type = {
	PyObject_HEAD_INIT(NULL)
	0,
	"ContextMethod",
	sizeof(ContextMethod),
	0,
	(destructor)cm_dealloc,				/* tp_dealloc */
	0,						/* tp_print */
	0,						/* tp_getattr */
	0,						/* tp_setattr */
	0,						/* tp_compare */
	0,						/* tp_repr */
	0,						/* tp_as_number */
	0,						/* tp_as_sequence */
	0,						/* tp_as_mapping */
	0,						/* tp_hash */
	0,						/* tp_call */
	0,						/* tp_str */
	PyObject_GenericGetAttr,			/* tp_getattro */
	0,						/* tp_setattro */
	0,						/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,	/* tp_flags */
	ContextMethod_doc,				/* tp_doc */
	0,						/* tp_traverse */
	0,						/* tp_clear */
	0,						/* tp_richcompare */
	0,						/* tp_weaklistoffset */
	0,						/* tp_iter */
	0,						/* tp_iternext */
	0,						/* tp_methods */
	0,						/* tp_members */
	0,						/* tp_getset */
	0,						/* tp_base */
	0,						/* tp_dict */
	cm_descr_get,					/* tp_descr_get */
	0,						/* tp_descr_set */
	0,						/* tp_dictoffset */
	cm_init,					/* tp_init */
	PyType_GenericAlloc,				/* tp_alloc */
	PyType_GenericNew,				/* tp_new */
	_PyObject_Del,					/* tp_free */
};

PyObject *
ContextMethod_New(PyObject *callable)
{
    ContextMethod *cm = (ContextMethod *)
        PyType_GenericAlloc(&ContextMethod_Type, 0);
    if (cm != NULL) {
        Py_INCREF(callable);
        cm->cm_callable = callable;
    }
    return (PyObject *)cm;
}

/* end of ContextMethod */


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

/* Provide tp_getattro and tp_setattro implementations that check to see
 * if the wrapped object's class is ContextAware or the descriptor that
 * implements the attribute is a ContextDescriptor. If either of these
 * holds true, then the descriptor is used with the wrapper's self instead
 * of the object's self.
 *
 * We use _PyType_Lookup to get descriptors directly from the class.
 * This is defined in Python/Objects/typeobject.c, and is part of the Python
 * internal API. It returns a borrowed reference, and doesn't set an
 * exception. It returns the descriptor from the class, rather than calling
 * tp_descr_get on the descriptor with a second argument of None (which most,
 * but not all, descriptors implement as returning the descriptor itself).
 *
 * _PyType_Lookup is about 20 lines of code, so we could reproduce it here if
 * we don't want to depend on the Internal API.
 */
static PyObject *
wrap_getattro(PyObject *self, PyObject *name)
{
    PyObject *wrapped;
    PyObject *descriptor;

    wrapped = Proxy_GET_OBJECT(self);
    if (wrapped == NULL) {
        PyErr_Format(PyExc_RuntimeError,
            "object is NULL; requested to get attribute '%s'",
            PyString_AS_STRING(name));
        return NULL;
    }
    descriptor = _PyType_Lookup(wrapped->ob_type, name);
    if (descriptor != NULL &&
        descriptor->ob_type->tp_descr_get != NULL &&
        (PyObject_TypeCheck(descriptor, &ContextDescriptorType) ||
         PyObject_TypeCheck(wrapped, &ContextAwareType))
        )
        return descriptor->ob_type->tp_descr_get(
                descriptor,
                self,
                PyObject_Type(wrapped));

    return PyObject_GetAttr(wrapped, name);
}

static int
wrap_setattro(PyObject *self, PyObject *name, PyObject *value)
{
    PyObject *wrapped;
    PyObject *descriptor;

    wrapped = Proxy_GET_OBJECT(self);
    if (wrapped == NULL) {
        PyErr_Format(PyExc_RuntimeError,
            "object is NULL; requested to set attribute '%s'",
            PyString_AS_STRING(name));
        return -1;
    }
    descriptor = _PyType_Lookup(wrapped->ob_type, name);
    if (descriptor != NULL &&
        (PyObject_TypeCheck(descriptor, &ContextDescriptorType) ||
         PyObject_TypeCheck(wrapped, &ContextAwareType)) &&
        descriptor->ob_type->tp_descr_set != NULL
        )
        return descriptor->ob_type->tp_descr_set(descriptor, self, value);
    return PyObject_SetAttr(wrapped, name, value);
}

/* What follows are specific implementations of tp_-slots for those slots
 * for which we want to support rebinding of ContextDescriptors.
 *
 * The macros that immediately follow provide boilerplate code that is
 * common to many of the implementations.
 * In FILLSLOT, NAME is a C string of the name of the slot's associated
 * attribute. BADVAL is the value to return on failure: NULL or -1 depending
 * whether the API returns an int or a PyObject *.
 *
 */
#define FILLSLOTDEFS \
    PyObject *wrapped; \
    PyObject *descriptor;

#define FILLSLOT(NAME, BADVAL) \
    wrapped = Proxy_GET_OBJECT(self); \
    if (wrapped == NULL) { \
        PyErr_Format(PyExc_RuntimeError, \
                     "object is NULL; requested to get attribute '%s'",\
                     (NAME)); \
            return (BADVAL); \
    } \
    descriptor = _PyType_Lookup(wrapped->ob_type,\
                    PyString_FromString((NAME))); \
    if (descriptor != NULL && \
        descriptor->ob_type->tp_descr_get != NULL && \
        (PyObject_TypeCheck(descriptor, &ContextDescriptorType) || \
            PyObject_TypeCheck(wrapped, &ContextAwareType))\
        )

#define FILLSLOTBASE(NAME) \
    FILLSLOTDEFS \
    FILLSLOT(NAME, NULL)

#define FILLSLOTBASEINT(NAME) \
    FILLSLOTDEFS \
    FILLSLOT(NAME, -1)

#define REBOUNDDESCRIPTOR \
    descriptor->ob_type->tp_descr_get( \
                    descriptor, self, PyObject_Type(wrapped))


/* Sequence/mapping protocol: __len__, __getitem__, __setitem__
 */

static int
wrap_length(PyObject *self)
{
    PyObject *res;
    int len;
    FILLSLOTBASEINT("__len__") {
        res = PyObject_CallFunctionObjArgs(REBOUNDDESCRIPTOR, NULL);
        if (res == NULL)
            return -1;
        len = (int)PyInt_AsLong(res);
        Py_DECREF(res);
        return len;
    }
    return PyObject_Length(wrapped);
}

static PyObject *
wrap_getitem(PyObject *self, PyObject *v) {
    FILLSLOTBASE("__getitem__")
        return PyObject_CallFunctionObjArgs(REBOUNDDESCRIPTOR, v, NULL);
    return PyObject_GetItem(wrapped, v);
}

static int
wrap_setitem(PyObject *self, PyObject *key, PyObject *value)
{
    PyObject *res;
    FILLSLOTDEFS

    if (value == NULL) {
        FILLSLOT("__delitem__", -1) {
            res = PyObject_CallFunctionObjArgs(REBOUNDDESCRIPTOR, key, NULL);
            if (res == NULL)
                return -1;
            Py_DECREF(res);
            return 0;
        }
        return PyObject_DelItem(wrapped, key);
    } else {
        FILLSLOT("__setitem__", -1) {
            res = PyObject_CallFunctionObjArgs(
                            REBOUNDDESCRIPTOR, key, value, NULL);
            if (res == NULL)
                return -1;
            Py_DECREF(res);
            return 0;
        }
        return PyObject_SetItem(Proxy_GET_OBJECT(self), key, value);
    }
}

/* Iterator protocol: __iter__, next
 */

static PyObject *
wrap_iter(PyObject *self)
{
    FILLSLOTBASE("__iter__")
        return PyObject_CallFunctionObjArgs(REBOUNDDESCRIPTOR, NULL);
    return PyObject_GetIter(wrapped);
}

static PyObject *
wrap_iternext(PyObject *self)
{
    FILLSLOTBASE("next")
        return PyObject_CallFunctionObjArgs(REBOUNDDESCRIPTOR, NULL);
    return PyIter_Next(Proxy_GET_OBJECT(self));
}

/* __contains__
 */

static int
wrap_contains(PyObject *self, PyObject *value)
{
    PyObject *res;
    int result;
    FILLSLOTBASEINT("__contains__") {
        res = PyObject_CallFunctionObjArgs(REBOUNDDESCRIPTOR, value, NULL);
        if (res == NULL)
            return -1;
        result = PyObject_IsTrue(res);
        Py_DECREF(res);
        return result;
    }
    return PySequence_Contains(wrapped, value);
}

/* Other miscellaneous methods: __call__, __str__
 */

static PyObject *
wrap_call(PyObject *self, PyObject *args, PyObject *kw)
{
    FILLSLOTDEFS

    if (kw) {
        FILLSLOT("__call__", NULL)
            return PyEval_CallObjectWithKeywords(REBOUNDDESCRIPTOR, args, kw);
        return PyEval_CallObjectWithKeywords(wrapped, args, kw);
    } else {
        FILLSLOT("__call__", NULL)
            return PyObject_CallObject(REBOUNDDESCRIPTOR, args);
        return PyObject_CallObject(wrapped, args);
    }
}

static PyObject *
wrap_str(PyObject *self) {
    FILLSLOTBASE("__str__")
        return PyObject_CallFunctionObjArgs(REBOUNDDESCRIPTOR, NULL);
    return PyObject_Str(wrapped);
}

/*
 * Normal methods
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

static PySequenceMethods
wrap_as_sequence = {
    wrap_length,				/* sq_length */
    0,						/* sq_concat */
    0,						/* sq_repeat */
    0,						/* sq_item */
    0,						/* sq_slice */
    0,						/* sq_ass_item */
    0,						/* sq_ass_slice */
    wrap_contains,				/* sq_contains */
};

static PyMappingMethods
wrap_as_mapping = {
    wrap_length,				/* mp_length */
    wrap_getitem,				/* mp_subscript */
    wrap_setitem,				/* mp_ass_subscript */
};

statichere PyTypeObject
WrapperType = {
    PyObject_HEAD_INIT(NULL)
    0,
    "wrapper.Wrapper",
    sizeof(WrapperObject),
    0,
    wrap_dealloc,				/* tp_dealloc */
    0,						/* tp_print */
    0,						/* tp_getattr */
    0,						/* tp_setattr */
    0,						/* tp_compare */
    0,						/* tp_repr */
    0,						/* tp_as_number */
    &wrap_as_sequence,				/* tp_as_sequence */
    &wrap_as_mapping,				/* tp_as_mapping */
    0,						/* tp_hash */
    wrap_call,					/* tp_call */
    wrap_str,					/* tp_str */
    wrap_getattro,				/* tp_getattro */
    wrap_setattro,				/* tp_setattro */
    0,						/* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC
        | Py_TPFLAGS_BASETYPE,			/* tp_flags */
    0,						/* tp_doc */
    wrap_traverse,				/* tp_traverse */
    wrap_clear,					/* tp_clear */
    0,						/* tp_richcompare */
    0,						/* tp_weaklistoffset */
    wrap_iter,					/* tp_iter */
    wrap_iternext,				/* tp_iternext */
    wrap_methods,				/* tp_methods */
    0,						/* tp_members */
    0,						/* tp_getset */
    0,						/* tp_base */
    0,						/* tp_dict */
    0,						/* tp_descr_get */
    0,						/* tp_descr_set */
    0,						/* tp_dictoffset */
    wrap_init,					/* tp_init */
    0, /*PyType_GenericAlloc,*/			/* tp_alloc */
    wrap_new,					/* tp_new */
    0, /*_PyObject_GC_Del,*/			/* tp_free */
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
        return missing_wrapper("getinnerwrapper");
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
"wrappers with 'wrapper' at the head.  Returns the object if 'wrapper'\n"
"isn't a wrapper at all.";

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
"Replace the wrapped object with object.";

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

    WrapperType.tp_base = ProxyType;
    WrapperType.tp_alloc = PyType_GenericAlloc;
    WrapperType.tp_free = _PyObject_GC_Del;
    if (PyType_Ready(&WrapperType) < 0)
        return;

    Py_INCREF(&WrapperType);
    PyModule_AddObject(m, "Wrapper", (PyObject *)&WrapperType);

    if (PyType_Ready(&ContextAwareType) < 0)
        return;
    Py_INCREF(&ContextAwareType);
    PyModule_AddObject(m, "ContextAware", (PyObject *)&ContextAwareType);

    if (PyType_Ready(&ContextDescriptorType) < 0)
        return;
    Py_INCREF(&ContextDescriptorType);
    PyModule_AddObject(m, "ContextDescriptor",
                       (PyObject *)&ContextDescriptorType);

    ContextMethod_Type.tp_base = &ContextDescriptorType;
    if (PyType_Ready(&ContextMethod_Type) < 0)
        return;
    Py_INCREF(&ContextMethod_Type);
    PyModule_AddObject(m, "ContextMethod", (PyObject *)&ContextMethod_Type);

    ContextProperty_Type.tp_base = &ContextDescriptorType;
    if (PyType_Ready(&ContextProperty_Type) < 0)
        return;
    Py_INCREF(&ContextProperty_Type);
    PyModule_AddObject(m, "ContextProperty",
                       (PyObject *)&ContextProperty_Type);

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

#include <stdio.h>
#include <Python.h>
#include "structmember.h"
#include "modsupport.h"
#include "zope/proxy/proxy.h"
#define WRAPPER_MODULE
#include "zope/context/wrapper.h"

#define Wrapper_Check(wrapper)   (PyObject_TypeCheck(wrapper, &WrapperType))

#define Wrapper_GetObject(wrapper) Proxy_GET_OBJECT((wrapper))

#define Wrapper_GetContext(wrapper) \
        (((WrapperObject *)wrapper)->wrap_context)

#define Wrapper_GetDict(wrapper) \
        (((WrapperObject *)wrapper)->wrap_dict)

static PyTypeObject WrapperType;
static PyTypeObject ContextAwareType;

static PyObject *empty_tuple = NULL;

/* We need to use PyStrings for the various python special method names,
 * such as __len__ and next and __getitem__.
 * At module initialisation, we create the strings, and cache them here.
 */
static PyObject *SlotStrings[10];
#define LEN_IDX 0
#define NONZERO_IDX 1
#define GETITEM_IDX 2
#define SETITEM_IDX 3
#define DELITEM_IDX 4
#define ITER_IDX 5
#define NEXT_IDX 6
#define CONTAINS_IDX 7
#define CALL_IDX 8
#define STR_IDX 9


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
    0,/*PyType_GenericNew,*/				/* tp_new */
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
    0, /*PyType_GenericNew,*/			/* tp_new */
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
    VISIT(prop_doc);

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
	0, /*PyObject_GenericGetAttr,*/			/* tp_getattro */
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
	0, /*PyType_GenericAlloc,*/			/* tp_alloc */
	0, /*PyType_GenericNew,*/			/* tp_new */
	0, /*_PyObject_GC_Del,*/			/* tp_free */
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
cm_dealloc(ContextMethod *cm)
{
    _PyObject_GC_UNTRACK((PyObject *)cm);
    Py_XDECREF(cm->cm_callable);
    ContextDescriptorType.tp_dealloc((PyObject *)cm);
}

static int
cm_traverse(ContextMethod *cm, visitproc visit, void *arg)
{
    if (!cm->cm_callable)
        return 0;
    return visit(cm->cm_callable, arg);
}

static int
cm_clear(ContextMethod *cm)
{
    Py_XDECREF(cm->cm_callable);
    cm->cm_callable = NULL;

    return 0;
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

    if (!PyArg_UnpackTuple(args, "ContextMethod", 1, 1, &callable))
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
	0, /*PyObject_GenericGetAttr,*/			/* tp_getattro */
	0,						/* tp_setattro */
	0,						/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE |
			    Py_TPFLAGS_HAVE_GC,		/* tp_flags */
	ContextMethod_doc,				/* tp_doc */
	(traverseproc)cm_traverse,			/* tp_traverse */
	(inquiry)cm_clear,				/* tp_clear */
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
	0, /*PyType_GenericAlloc,*/			/* tp_alloc */
	0, /*PyType_GenericNew,*/			/* tp_new */
	0, /*_PyObject_GC_Del,*/				/* tp_free */
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
        result = ProxyType.tp_new(type, proxyargs, NULL);
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
        if (ProxyType.tp_init(self, proxyargs, NULL) < 0)
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
 *
 * However, Guido says that it is ok to use _PyType_Lookup, and that the
 * function isn't going to go away.
 */


/* A variant of _PyType_Lookup that doesn't look in WrapperType or ProxyType.
 *
 * The argument is_reduce is 1 iff name is "__reduce__".
 * If is_reduce is 1, we may look in WrapperType.
 */
PyObject *
WrapperType_Lookup(PyTypeObject *type, PyObject *name, int is_reduce)
{
    int i, n;
    PyObject *mro, *res, *base, *dict;

    /* Look in tp_dict of types in MRO */
    mro = type->tp_mro;

    /* If mro is NULL, the type is either not yet initialized
       by PyType_Ready(), or already cleared by type_clear().
       Either way the safest thing to do is to return NULL. */
    if (mro == NULL)
        return NULL;

    assert(PyTuple_Check(mro));
    n = PyTuple_GET_SIZE(mro);

    for (i = 0; i < n; i++) {
        base = PyTuple_GET_ITEM(mro, i);

        if (((PyTypeObject *)base) != &ProxyType &&
            (((PyTypeObject *)base) != &WrapperType || is_reduce)) {
            if (PyClass_Check(base))
                dict = ((PyClassObject *)base)->cl_dict;
            else {
                assert(PyType_Check(base));
                dict = ((PyTypeObject *)base)->tp_dict;
            }
            assert(dict && PyDict_Check(dict));
            res = PyDict_GetItem(dict, name);
            if (res != NULL)
                return res;
        }
    }
    return NULL;
}


static PyObject *
wrap_getattro(PyObject *self, PyObject *name)
{
    PyObject *wrapped;
    PyObject *descriptor;
    PyObject *wrapped_type;
    PyObject *res = NULL;
    char *name_as_string;

#ifdef Py_USING_UNICODE
    /* The Unicode to string conversion is done here because the
       existing tp_getattro slots expect a string object as name
       and we wouldn't want to break those. */
    if (PyUnicode_Check(name)) {
        name = PyUnicode_AsEncodedString(name, NULL, NULL);
        if (name == NULL)
            return NULL;
    }
    else
#endif
    if (!PyString_Check(name)){
        PyErr_SetString(PyExc_TypeError, "attribute name must be string");
        return NULL;
    }
    else
        Py_INCREF(name);

    name_as_string = PyString_AS_STRING(name);
    wrapped = Proxy_GET_OBJECT(self);
    if (wrapped == NULL) {
        PyErr_Format(PyExc_RuntimeError,
            "object is NULL; requested to get attribute '%s'",
            name_as_string);
        goto finally;
    }
    if (strcmp(name_as_string, "__class__") != 0) {

        descriptor = WrapperType_Lookup(
                self->ob_type, name,
                strcmp(name_as_string, "__reduce__") == 0);
        if (descriptor != NULL) {
            if (PyType_HasFeature(descriptor->ob_type, Py_TPFLAGS_HAVE_CLASS)
                && descriptor->ob_type->tp_descr_get != NULL) {
                res = descriptor->ob_type->tp_descr_get(
                        descriptor,
                        self,
                        (PyObject *)self->ob_type);
            } else {
                Py_INCREF(descriptor);
                res = descriptor;
            }
            goto finally;
        }

        descriptor = _PyType_Lookup(wrapped->ob_type, name);
        if (descriptor != NULL &&
            PyType_HasFeature(descriptor->ob_type, Py_TPFLAGS_HAVE_CLASS) &&
            descriptor->ob_type->tp_descr_get != NULL &&
            (PyObject_TypeCheck(descriptor, &ContextDescriptorType) ||
             PyObject_TypeCheck(wrapped, &ContextAwareType)
            )) {
            wrapped_type = (PyObject *)wrapped->ob_type;
            if (wrapped_type == NULL)
                goto finally;
            res = descriptor->ob_type->tp_descr_get(
                    descriptor,
                    self,
                    wrapped_type);
            goto finally;
        }
    }
    res = PyObject_GetAttr(wrapped, name);
finally:
    Py_DECREF(name);
    return res;
}

static int
wrap_setattro(PyObject *self, PyObject *name, PyObject *value)
{
    PyObject *wrapped;
    PyObject *descriptor;
    int res = -1;

#ifdef Py_USING_UNICODE
    /* The Unicode to string conversion is done here because the
       existing tp_setattro slots expect a string object as name
       and we wouldn't want to break those. */
    if (PyUnicode_Check(name)) {
        name = PyUnicode_AsEncodedString(name, NULL, NULL);
        if (name == NULL)
            return -1;
    }
    else
#endif
    if (!PyString_Check(name)){
        PyErr_SetString(PyExc_TypeError, "attribute name must be string");
        return -1;
    }
    else
        Py_INCREF(name);

    descriptor = WrapperType_Lookup(self->ob_type, name, 0);
    if (descriptor != NULL) {
        if (PyType_HasFeature(descriptor->ob_type, Py_TPFLAGS_HAVE_CLASS) &&
            descriptor->ob_type->tp_descr_set != NULL) {
            res = descriptor->ob_type->tp_descr_set(descriptor, self, value);
        } else {
            PyErr_Format(PyExc_TypeError,
                "Tried to set attribute '%s' on wrapper, but it is not"
                " a data descriptor", PyString_AS_STRING(name));
        }
        goto finally;
    }

    wrapped = Proxy_GET_OBJECT(self);
    if (wrapped == NULL) {
        PyErr_Format(PyExc_RuntimeError,
            "object is NULL; requested to set attribute '%s'",
            PyString_AS_STRING(name));
        goto finally;
    }
    descriptor = _PyType_Lookup(wrapped->ob_type, name);
    if (descriptor != NULL &&
        PyType_HasFeature(descriptor->ob_type, Py_TPFLAGS_HAVE_CLASS) &&
        (PyObject_TypeCheck(descriptor, &ContextDescriptorType) ||
         PyObject_TypeCheck(wrapped, &ContextAwareType)) &&
        descriptor->ob_type->tp_descr_set != NULL
        )
        res = descriptor->ob_type->tp_descr_set(descriptor, self, value);
    else
        res = PyObject_SetAttr(wrapped, name, value);
finally:
    Py_DECREF(name);
    return res;
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
    PyObject *descriptor; \
    PyObject *wrapped_type;

#define FILLSLOTIF(BADVAL) \
    if (descriptor != NULL && \
        PyType_HasFeature(descriptor->ob_type, Py_TPFLAGS_HAVE_CLASS) && \
        descriptor->ob_type->tp_descr_get != NULL && \
        (PyObject_TypeCheck(descriptor, &ContextDescriptorType) || \
            PyObject_TypeCheck(wrapped, &ContextAwareType))\
        ) { \
        wrapped_type = (PyObject *) wrapped->ob_type; \
        if (wrapped_type == NULL) \
             return (BADVAL); \
        descriptor = descriptor->ob_type->tp_descr_get( \
                    descriptor, self, wrapped_type); \
        if (descriptor == NULL) \
             return (BADVAL);

#define FILLSLOT(NAME, IDX, BADVAL) \
    wrapped = Proxy_GET_OBJECT(self); \
    if (wrapped == NULL) { \
        PyErr_Format(PyExc_RuntimeError, \
                     "object is NULL; requested to get attribute '%s'",\
                     (NAME)); \
            return (BADVAL); \
    } \
    descriptor = _PyType_Lookup(wrapped->ob_type, SlotStrings[IDX]);\
    FILLSLOTIF(BADVAL)

/* Concerning the last two lines of the above macro:
 * Calling tp_descr_get returns a new reference.
 * We need to decref it once we've finished using it.
 * It will be available in the 'descriptor' variable.
 * tp_descr_get should never return NULL. So, we can use
 * Py_DECREF on the new value of 'descriptor'.
 */

#define FILLSLOTBASE(NAME, IDX) \
    FILLSLOTDEFS \
    FILLSLOT(NAME, IDX, NULL)

#define FILLSLOTBASEINT(NAME, IDX) \
    FILLSLOTDEFS \
    FILLSLOT(NAME, IDX, -1)


/* Sequence/mapping protocol: __len__, __getitem__, __setitem__
 */

static int
wrap_length(PyObject *self)
{
    PyObject *res;
    int len;
    FILLSLOTBASEINT("__len__", LEN_IDX)
        res = PyObject_CallFunctionObjArgs(descriptor, NULL);
        Py_DECREF(descriptor);
        if (res == NULL)
            return -1;
        len = (int)PyInt_AsLong(res);
        Py_DECREF(res);
        return len;
    }
    return PyObject_Length(wrapped);
}

static int
wrap_nonzero(PyObject *self)
{
    PyObject *res;
    int result;
    PyObject *wrapped;
    PyObject *descriptor;
    PyObject *wrapped_type;

    wrapped = Proxy_GET_OBJECT(self);
    if (wrapped == NULL) {
        PyErr_Format(PyExc_RuntimeError,
                     "object is NULL; requested to get attribute '__nonzero__'"
                     );
            return -1;
    }
    descriptor = WrapperType_Lookup(self->ob_type, SlotStrings[LEN_IDX], 0);
    if (descriptor != NULL) {
        /* There's a __len__ defined in a wrapper subclass, so we need
         * to call that.
         */
        if (PyType_HasFeature(descriptor->ob_type, Py_TPFLAGS_HAVE_CLASS)
            && descriptor->ob_type->tp_descr_get != NULL) {
            descriptor = descriptor->ob_type->tp_descr_get(
                            descriptor,
                            self,
                            (PyObject *)self->ob_type);
            if (descriptor == NULL)
                return -1;
            res = PyObject_CallFunctionObjArgs(descriptor, NULL);
            Py_DECREF(descriptor);
        } else {
            res = PyObject_CallFunctionObjArgs(descriptor, self, NULL);
        }
        if (res == NULL)
            return -1;
        result = PyObject_IsTrue(res);
        Py_DECREF(res);
        return result;
    }

    descriptor = _PyType_Lookup(wrapped->ob_type, SlotStrings[NONZERO_IDX]);
    if (descriptor == NULL)
        descriptor = _PyType_Lookup(wrapped->ob_type, SlotStrings[LEN_IDX]);
    FILLSLOTIF(-1)
        res = PyObject_CallFunctionObjArgs(descriptor, NULL);
        Py_DECREF(descriptor);
        if (res == NULL)
            return -1;
        result = PyObject_IsTrue(res);
        Py_DECREF(res);
        return result;
    }
    return PyObject_IsTrue(wrapped);
}

static PyObject *
wrap_getitem(PyObject *self, PyObject *v) {
    PyObject *retval;
    FILLSLOTBASE("__getitem__", GETITEM_IDX)
        retval = PyObject_CallFunctionObjArgs(descriptor, v, NULL);
        Py_DECREF(descriptor);
        return retval;
    }
    return PyObject_GetItem(wrapped, v);
}

static int
wrap_setitem(PyObject *self, PyObject *key, PyObject *value)
{
    PyObject *res;
    FILLSLOTDEFS

    if (value == NULL) {
        FILLSLOT("__delitem__", DELITEM_IDX, -1)
            res = PyObject_CallFunctionObjArgs(descriptor, key, NULL);
            Py_DECREF(descriptor);
            if (res == NULL)
                return -1;
            Py_DECREF(res);
            return 0;
        }
        return PyObject_DelItem(wrapped, key);
    } else {
        FILLSLOT("__setitem__", SETITEM_IDX, -1)
            res = PyObject_CallFunctionObjArgs(descriptor, key, value, NULL);
            Py_DECREF(descriptor);
            if (res == NULL)
                return -1;
            Py_DECREF(res);
            return 0;
        }
        return PyObject_SetItem(wrapped, key, value);
    }
}

/* Iterator protocol: __iter__, next
 */

static PyObject *
wrap_iter(PyObject *self)
{
    PyObject *retval;
    FILLSLOTBASE("__iter__", ITER_IDX)
        retval = PyObject_CallFunctionObjArgs(descriptor, NULL);
        Py_DECREF(descriptor);
        return retval;
    }
    return PyObject_GetIter(wrapped);
}

static PyObject *
wrap_iternext(PyObject *self)
{
    PyObject *retval;
    FILLSLOTBASE("next", NEXT_IDX)
        retval = PyObject_CallFunctionObjArgs(descriptor, NULL);
        Py_DECREF(descriptor);
        return retval;
    }
    return PyIter_Next(wrapped);
}

/* __contains__
 */

static int
wrap_contains(PyObject *self, PyObject *value)
{
    PyObject *res;
    int result;
    FILLSLOTBASEINT("__contains__", CONTAINS_IDX)
        res = PyObject_CallFunctionObjArgs(descriptor, value, NULL);
        Py_DECREF(descriptor);
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
    PyObject *retval;
    FILLSLOTDEFS

    if (kw) {
        FILLSLOT("__call__", CALL_IDX, NULL)
            retval = PyEval_CallObjectWithKeywords(descriptor, args, kw);
            Py_DECREF(descriptor);
            return retval;
        }
        return PyEval_CallObjectWithKeywords(wrapped, args, kw);
    } else {
        FILLSLOT("__call__", CALL_IDX, NULL)
            retval = PyObject_CallObject(descriptor, args);
            Py_DECREF(descriptor);
            return retval;
        }
        return PyObject_CallObject(wrapped, args);
    }
}

static PyObject *
wrap_str(PyObject *self) {
    PyObject *retval;

    FILLSLOTBASE("__str__", STR_IDX)
        retval =PyObject_CallFunctionObjArgs(descriptor, NULL);
        Py_DECREF(descriptor);
        return retval;
    }
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

static PyNumberMethods
wrap_as_number ={
    0,					/* nb_add */
    0,					/* nb_subtract */
    0,					/* nb_multiply */
    0,					/* nb_divide */
    0,					/* nb_remainder */
    0,					/* nb_divmod */
    0,					/* nb_power */
    0,					/* nb_negative */
    0,					/* nb_positive */
    0,					/* nb_absolute */
    wrap_nonzero,			/* nb_nonzero */
    0,					/* nb_invert */
    0,					/* nb_lshift */
    0,					/* nb_rshift */
    0,					/* nb_and */
    0,					/* nb_xor */
    0,					/* nb_or */
    0,					/* nb_coerce */
    0,					/* nb_int */
    0,					/* nb_long */
    0,					/* nb_float */
    0,					/* nb_oct */
    0,					/* nb_hex */

    /* Added in release 2.0 */
    /* These require the Py_TPFLAGS_HAVE_INPLACEOPS flag */
    0,					/* nb_inplace_add */
    0,					/* nb_inplace_subtract */
    0,					/* nb_inplace_multiply */
    0,					/* nb_inplace_divide */
    0,					/* nb_inplace_remainder */
    0,					/* nb_inplace_power */
    0,					/* nb_inplace_lshift */
    0,					/* nb_inplace_rshift */
    0,					/* nb_inplace_and */
    0,					/* nb_inplace_xor */
    0,					/* nb_inplace_or */

    /* Added in release 2.2 */
    /* These require the Py_TPFLAGS_HAVE_CLASS flag */
    0,					/* nb_floor_divide */
    0,					/* nb_true_divide */
    0,					/* nb_inplace_floor_divide */
    0,					/* nb_inplace_true_divide */
};

statichere PyTypeObject
WrapperType = {
    PyObject_HEAD_INIT(NULL)
    0,
    "wrapper.Wrapper",
    sizeof(WrapperObject),
    0,
    wrap_dealloc,					/* tp_dealloc */
    0,							/* tp_print */
    0,							/* tp_getattr */
    0,							/* tp_setattr */
    0,							/* tp_compare */
    0,							/* tp_repr */
    &wrap_as_number,					/* tp_as_number */
    &wrap_as_sequence,					/* tp_as_sequence */
    &wrap_as_mapping,					/* tp_as_mapping */
    0,							/* tp_hash */
    wrap_call,						/* tp_call */
    wrap_str,						/* tp_str */
    wrap_getattro,					/* tp_getattro */
    wrap_setattro,					/* tp_setattro */
    0,							/* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC
        | Py_TPFLAGS_CHECKTYPES | Py_TPFLAGS_BASETYPE,	/* tp_flags */
    0,							/* tp_doc */
    wrap_traverse,					/* tp_traverse */
    wrap_clear,						/* tp_clear */
    0,							/* tp_richcompare */
    0,							/* tp_weaklistoffset */
    wrap_iter,						/* tp_iter */
    wrap_iternext,					/* tp_iternext */
    wrap_methods,					/* tp_methods */
    0,							/* tp_members */
    0,							/* tp_getset */
    0,							/* tp_base */
    0,							/* tp_dict */
    0,							/* tp_descr_get */
    0,							/* tp_descr_set */
    0,							/* tp_dictoffset */
    wrap_init,						/* tp_init */
    0, /*PyType_GenericAlloc,*/				/* tp_alloc */
    wrap_new,						/* tp_new */
    0, /*_PyObject_GC_Del,*/				/* tp_free */
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
    &WrapperType,
    &ContextDescriptorType,
    &ContextAwareType,
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

static PyObject *api_object = NULL;

void
initwrapper(void)
{
    PyObject *m;

    if (Proxy_Import() < 0)
        return;

    m = Py_InitModule3("wrapper", module_functions, module___doc__);
    if (m == NULL)
        return;

    SlotStrings[LEN_IDX] = PyString_InternFromString("__len__");
    SlotStrings[NONZERO_IDX] = PyString_InternFromString("__nonzero__");
    SlotStrings[GETITEM_IDX] = PyString_InternFromString("__getitem__");
    SlotStrings[SETITEM_IDX] = PyString_InternFromString("__setitem__");
    SlotStrings[DELITEM_IDX] = PyString_InternFromString("__delitem__");
    SlotStrings[ITER_IDX] = PyString_InternFromString("__iter__");
    SlotStrings[NEXT_IDX] = PyString_InternFromString("next");
    SlotStrings[CONTAINS_IDX] = PyString_InternFromString("__contains__");
    SlotStrings[CALL_IDX] = PyString_InternFromString("__call__");
    SlotStrings[STR_IDX] = PyString_InternFromString("__str__");

    WrapperType.tp_base = &ProxyType;
    WrapperType.tp_alloc = PyType_GenericAlloc;
    WrapperType.tp_free = _PyObject_GC_Del;
    if (PyType_Ready(&WrapperType) < 0)
        return;

    Py_INCREF(&WrapperType);
    PyModule_AddObject(m, "Wrapper", (PyObject *)&WrapperType);

    ContextAwareType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&ContextAwareType) < 0)
        return;
    Py_INCREF(&ContextAwareType);
    PyModule_AddObject(m, "ContextAware", (PyObject *)&ContextAwareType);

    ContextDescriptorType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&ContextDescriptorType) < 0)
        return;
    Py_INCREF(&ContextDescriptorType);
    PyModule_AddObject(m, "ContextDescriptor",
                       (PyObject *)&ContextDescriptorType);

    ContextMethod_Type.tp_new = PyType_GenericNew;
    ContextMethod_Type.tp_base = &ContextDescriptorType;
    ContextMethod_Type.tp_getattro = PyObject_GenericGetAttr;
    ContextMethod_Type.tp_alloc = PyType_GenericAlloc;
    ContextMethod_Type.tp_free = _PyObject_GC_Del;
    if (PyType_Ready(&ContextMethod_Type) < 0)
        return;
    Py_INCREF(&ContextMethod_Type);
    PyModule_AddObject(m, "ContextMethod", (PyObject *)&ContextMethod_Type);

    ContextProperty_Type.tp_new = PyType_GenericNew;
    ContextProperty_Type.tp_base = &ContextDescriptorType;
    ContextProperty_Type.tp_getattro = PyObject_GenericGetAttr;
    ContextProperty_Type.tp_free = _PyObject_GC_Del;
    ContextProperty_Type.tp_alloc = PyType_GenericAlloc;
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

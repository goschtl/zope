#include <Python.h>
#include "structmember.h"
#include "modsupport.h"
#include "zope/proxy/proxy.h"
#include "zope/proxy/context/wrapper.h"
#define DECORATOR_MODULE
#include "zope/proxy/context/decorator.h"

/* XXX perhaps all these wrapper args should be renamed to decorator? */
#define Decorator_Check(wrapper)  (PyObject_TypeCheck(wrapper, &DecoratorType))

#define Decorator_GetObject(wrapper) Proxy_GET_OBJECT((wrapper))

#define Decorator_GetMixinFactory(wrapper) \
    (((DecoratorObject *)wrapper)->mixin_factory)

#define Decorator_GetMixin(wrapper) \
    (((DecoratorObject *)wrapper)->mixin)

#define Decorator_GetNames(wrapper) \
    (((DecoratorObject *)wrapper)->names)

#define Decorator_GetNamesDict(wrapper) \
    (((DecoratorObject *)wrapper)->names_dict)

static PyTypeObject DecoratorType;

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

/* Helper for decorate_new/decorate_init; return the base class args tuple
 * from the incoming args tuple.  Returns a new reference.
 */
static PyObject *
create_wrapper_args(PyObject *args, PyObject *object, PyObject *context)
{
    if (PyTuple_GET_SIZE(args) == 1 || PyTuple_GET_SIZE(args) == 2)
        Py_INCREF(args);
    else if (context == NULL) {
        args = PyTuple_New(1);
        if (args != NULL) {
            Py_INCREF(object);
            PyTuple_SET_ITEM(args, 0, object);
        }
    } else {
        args = PyTuple_New(2);
        if (args != NULL) {
            Py_INCREF(object);
            PyTuple_SET_ITEM(args, 0, object);
            Py_INCREF(context);
            PyTuple_SET_ITEM(args, 1, context);
        }
    }
    return args;
}

/*
 *   Slot methods.
 */

static PyObject *
decorate_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result = NULL;
    PyObject *context;
    PyObject *object;
    PyObject *mixin_factory;
    PyObject *names;

    if (PyArg_UnpackTuple(args, "__new__", 1, 4, &object, &context,
            &mixin_factory, &names)) {
        PyObject *wrapperargs = create_wrapper_args(args, object, context);
        if (wrapperargs == NULL)
            goto finally;
        result = WrapperType.tp_new(type, wrapperargs, NULL);
        Py_DECREF(wrapperargs);
    }
 finally:
    return result;
}

static int
decorate_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    int result = -1;
    PyObject *context = NULL;
    PyObject *wrapperargs = NULL;
    PyObject *object;
    PyObject *mixin_factory = NULL;
    PyObject *names = NULL;
    PyObject *fast_names = NULL;

    if (PyArg_UnpackTuple(args, "__init__", 1, 4, &object, &context,
            &mixin_factory, &names)) {
        PyObject *temp;
        int size;
        DecoratorObject *decorator = (DecoratorObject *)self;
        wrapperargs = create_wrapper_args(args, object, context);
        if (wrapperargs == NULL)
            goto finally;
        if (WrapperType.tp_init(self, wrapperargs, kwds) < 0)
            goto finally;
        /* XXX This might be a little weird: if a subclass initializes
         * XXX the following fields, we end up overwriting them, and clearing
         * XXX them if this __init__ is called with too few args.
         */
        if (decorator->mixin_factory != mixin_factory) {
            temp = decorator->mixin_factory;
            Py_XINCREF(mixin_factory);
            decorator->mixin_factory = mixin_factory;
            Py_XDECREF(temp);
        }
        /* Take the given names and force them to be in a tuple.
         * If the tuple is empty, names_dict should be NULL.
         * Otherwise, names_dict should have the names as keys.
         */
        if (names == NULL) {
            fast_names = empty_tuple;
            Py_INCREF(fast_names);
        } else {
            fast_names = PySequence_Tuple(names);
            if (fast_names == NULL) goto finally;
        }
        /* Check that the old value (if any) of decorator->names is disposed
         * of properly. This works even if decorator->names == fast_names.
         */
        temp = decorator->names;
        decorator->names = fast_names;
        Py_XDECREF(temp);

        size = PySequence_Fast_GET_SIZE(fast_names);
        if (size) {
            PyObject *names_dict = PyDict_New();
            int i;

            if (names_dict == NULL) goto finally;
            /* names_dict is private to this type, so there really shouldn't
             * be anything in it already.
             */
            decorator->names_dict = names_dict;
            for (i=0; i<size; ++i) {
                temp = PySequence_Fast_GET_ITEM(fast_names, i);
                if (!PyString_CheckExact(temp)) {
                    PyErr_SetString(PyExc_TypeError,
                                    "'names' must contain only strings.");
                    goto finally;
                }
                if (PyDict_SetItem(names_dict, temp, Py_None) != 0) {
                    goto finally;
                }
            }
        }
        /* otherwise, names == (), and names_dict == NULL */

        result = 0;
    }
 finally:
    Py_XDECREF(wrapperargs);
    return result;
}

static int
decorate_traverse(PyObject *self, visitproc visit, void *arg)
{
    int err = WrapperType.tp_traverse(self, visit, arg);

    if (!err && Decorator_GetMixinFactory(self) != NULL)
        err = visit(Decorator_GetMixinFactory(self), arg);

    if (!err && Decorator_GetMixin(self) != NULL)
        err = visit(Decorator_GetMixin(self), arg);
    if (!err && Decorator_GetNames(self) != NULL)
        err = visit(Decorator_GetNames(self), arg);
    if (!err && Decorator_GetNamesDict(self) != NULL)
        err = visit(Decorator_GetNamesDict(self), arg);

    return err;
}

static int
decorate_clear(PyObject *self)
{
    DecoratorObject *decorator = (DecoratorObject *)self;
    PyObject *temp;

    WrapperType.tp_clear(self);

    if ((temp = decorator->mixin_factory) != NULL) {
        decorator->mixin_factory = NULL;
        Py_DECREF(temp);
    }
    if ((temp = decorator->mixin) != NULL) {
        decorator->mixin = NULL;
        Py_DECREF(temp);
    }
    if ((temp = decorator->names) != NULL) {
        decorator->names = NULL;
        Py_DECREF(temp);
    }
    if ((temp = decorator->names_dict) != NULL) {
        decorator->names_dict = NULL;
        Py_DECREF(temp);
    }
    return 0;
}

static void
decorate_dealloc(PyObject *self)
{
    (void) decorate_clear(self);
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


#define DISPATCH_TO_DECORATOR(BADVAL) \
        if (PyErr_Occurred()) return (BADVAL); \
        /* We have a name.
         * If the mixin exists, dispatch the name to the mixin.
         * If the mixin doesn't exist, create it from the factory.
         */ \
        if (Decorator_GetMixin(self) != NULL) \
            wrapped = Decorator_GetMixin(self); \
        else if (Decorator_GetMixinFactory(self) != NULL) { \
            wrapped = PyObject_CallObject(Decorator_GetMixinFactory(self), \
                                          NULL); \
            if (wrapped == NULL) \
                return (BADVAL); \
            ((DecoratorObject *)self)->mixin = wrapped; \
        } else { \
            PyErr_SetString(PyExc_TypeError, \
                    "Cannot create mixin, as there is no mixin factory."); \
            return (BADVAL); \
        }

/* Perhaps we don't need to check that the namesdict is non-null, as it
 * will always have been created.
 */
#define MAYBE_DISPATCH_TO_DECORATOR_NAMEVAR(BADVAL) \
    if (Decorator_GetNamesDict(self) && \
            PyDict_GetItem(Decorator_GetNamesDict(self), name) != NULL) { \
      DISPATCH_TO_DECORATOR(BADVAL) \
    }

#define MAYBE_DISPATCH_TO_DECORATOR(NAME, BADVAL) \
    if (Decorator_GetNamesDict(self) && \
        PyDict_GetItem(Decorator_GetNamesDict(self), (NAME)) != NULL) { \
      DISPATCH_TO_DECORATOR(BADVAL) \
    }

static PyObject *
decorate_getattro(PyObject *self, PyObject *name)
{
    PyObject *wrapped;
    PyObject *descriptor;
    PyObject *wrapped_type;

    wrapped = Proxy_GET_OBJECT(self);
    if (wrapped == NULL) {
        PyErr_Format(PyExc_RuntimeError,
            "object is NULL; requested to get attribute '%s'",
            PyString_AS_STRING(name));
        return NULL;
    }
    MAYBE_DISPATCH_TO_DECORATOR_NAMEVAR(NULL)

    descriptor = _PyType_Lookup(wrapped->ob_type, name);
    if (descriptor != NULL &&
        descriptor->ob_type->tp_descr_get != NULL &&
        (PyObject_TypeCheck(descriptor, &ContextDescriptorType) ||
         PyObject_TypeCheck(wrapped, &ContextAwareType)) &&
        ! (PyString_Check(name)
           && strcmp(PyString_AS_STRING(name), "__class__") == 0)
        ) {

        wrapped_type = (PyObject *)wrapped->ob_type;
        if (wrapped_type == NULL)
            return NULL;
        return descriptor->ob_type->tp_descr_get(
                descriptor,
                self,
                wrapped_type);
    }
    return PyObject_GetAttr(wrapped, name);
}

static int
decorate_setattro(PyObject *self, PyObject *name, PyObject *value)
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
    MAYBE_DISPATCH_TO_DECORATOR_NAMEVAR(-1)
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
    PyObject *descriptor; \
    PyObject *wrapped_type;

#define FILLSLOTIF(BADVAL) \
    if (descriptor != NULL && \
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
    MAYBE_DISPATCH_TO_DECORATOR(SlotStrings[IDX], BADVAL) \
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
decorate_length(PyObject *self)
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
decorate_nonzero(PyObject *self)
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

    /* if __nonzero__ in names:
     *     dispatch to decorator
     * if __len__ in names:
     *     dispatch to decorator only if __nonzero__ not in object's class.
     *
     * if (namesdict != NULL and
     *     (namesdict['__nonzero__'] != NULL or
     *      (namesdict['__len__'] != NULL and
     *       not hasattr(type(wrapped), '__nonzero__')
     *      ))):
     *      dispatch to mixin
     */
    if (Decorator_GetNamesDict(self) &&
        (PyDict_GetItem(Decorator_GetNamesDict(self),
                       SlotStrings[NONZERO_IDX]) != NULL ||
         (PyDict_GetItem(Decorator_GetNamesDict(self),
                       SlotStrings[LEN_IDX]) != NULL &&
          _PyType_Lookup(wrapped->ob_type, SlotStrings[NONZERO_IDX]) == NULL
        ))) {
        DISPATCH_TO_DECORATOR(-1)
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
decorate_getitem(PyObject *self, PyObject *v) {
    PyObject *retval;
    FILLSLOTBASE("__getitem__", GETITEM_IDX)
        retval = PyObject_CallFunctionObjArgs(descriptor, v, NULL);
        Py_DECREF(descriptor);
        return retval;
    }
    return PyObject_GetItem(wrapped, v);
}

static int
decorate_setitem(PyObject *self, PyObject *key, PyObject *value)
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
decorate_iter(PyObject *self)
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
decorate_iternext(PyObject *self)
{
    PyObject *retval;
    FILLSLOTBASE("next", NEXT_IDX)
        retval = PyObject_CallFunctionObjArgs(descriptor, NULL);
        Py_DECREF(descriptor);
        return retval;
    }
    return PyIter_Next(Proxy_GET_OBJECT(self));
}

/* __contains__
 */

static int
decorate_contains(PyObject *self, PyObject *value)
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
decorate_call(PyObject *self, PyObject *args, PyObject *kw)
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
decorate_str(PyObject *self) {
    PyObject *retval;

    FILLSLOTBASE("__str__", STR_IDX)
        retval =PyObject_CallFunctionObjArgs(descriptor, NULL);
        Py_DECREF(descriptor);
        return retval;
    }
    return PyObject_Str(wrapped);
}

static PySequenceMethods
decorate_as_sequence = {
    decorate_length,				/* sq_length */
    0,						/* sq_concat */
    0,						/* sq_repeat */
    0,						/* sq_item */
    0,						/* sq_slice */
    0,						/* sq_ass_item */
    0,						/* sq_ass_slice */
    decorate_contains,				/* sq_contains */
};

static PyMappingMethods
decorate_as_mapping = {
    decorate_length,				/* mp_length */
    decorate_getitem,				/* mp_subscript */
    decorate_setitem,				/* mp_ass_subscript */
};

static PyNumberMethods
decorate_as_number ={
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
    decorate_nonzero,			/* nb_nonzero */
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
DecoratorType = {
    PyObject_HEAD_INIT(NULL)
    0,
    "decorator.Decorator",
    sizeof(DecoratorObject),
    0,
    decorate_dealloc,					/* tp_dealloc */
    0,							/* tp_print */
    0,							/* tp_getattr */
    0,							/* tp_setattr */
    0,							/* tp_compare */
    0,							/* tp_repr */
    &decorate_as_number,				/* tp_as_number */
    &decorate_as_sequence,				/* tp_as_sequence */
    &decorate_as_mapping,				/* tp_as_mapping */
    0,							/* tp_hash */
    decorate_call,					/* tp_call */
    decorate_str,					/* tp_str */
    decorate_getattro,					/* tp_getattro */
    decorate_setattro,					/* tp_setattro */
    0,							/* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC
        | Py_TPFLAGS_CHECKTYPES | Py_TPFLAGS_BASETYPE,	/* tp_flags */
    0,							/* tp_doc */
    decorate_traverse,					/* tp_traverse */
    decorate_clear,					/* tp_clear */
    0,							/* tp_richcompare */
    0,							/* tp_weaklistoffset */
    decorate_iter,					/* tp_iter */
    decorate_iternext,					/* tp_iternext */
    0,							/* tp_methods */
    0,							/* tp_members */
    0,							/* tp_getset */
    0,							/* tp_base */
    0,							/* tp_dict */
    0,							/* tp_descr_get */
    0,							/* tp_descr_set */
    0,							/* tp_dictoffset */
    decorate_init,					/* tp_init */
    0, /*PyType_GenericAlloc,*/				/* tp_alloc */
    decorate_new,					/* tp_new */
    0, /*_PyObject_GC_Del,*/				/* tp_free */
};


static PyObject *
create_decorator(PyObject *object, PyObject *context, PyObject *mixin_factory,
                 PyObject *names)
{
    PyObject *result = NULL;
    PyObject *args;

    args = PyTuple_New(5);
    if (args == NULL) return NULL;
    Py_INCREF(object);
    PyTuple_SET_ITEM(args, 0, object);

    if (!context) context = Py_None;
    Py_INCREF(context);
    PyTuple_SET_ITEM(args, 1, context);

    if (!mixin_factory) mixin_factory = Py_None;
    Py_INCREF(mixin_factory);
    PyTuple_SET_ITEM(args, 2, mixin_factory);

    if (!names) names = empty_tuple;
    Py_INCREF(names);
    PyTuple_SET_ITEM(args, 3, names);

    result = PyObject_CallObject((PyObject *)&DecoratorType, args);
    Py_DECREF(args);
    return result;
}

static int
api_check(PyObject *obj)
{
    return obj ? Decorator_Check(obj) : 0;
}

static PyObject *
api_create(PyObject *object, PyObject *context, PyObject *mixin_factory,
           PyObject *names)
{
    if (object == NULL) {
        PyErr_SetString(PyExc_ValueError,
                        "cannot create decorator around NULL");
        return NULL;
    }
    return create_decorator(object, context, mixin_factory, names);
}

static PyObject *
missing_decorator(const char *funcname)
{
    PyErr_Format(PyExc_RuntimeError,
                 "cannot pass NULL to DecoratorAPI.%s()", funcname);
    return NULL;
}

static int
check_decorator(PyObject *wrapper, const char *funcname)
{
    if (wrapper == NULL) {
        (void) missing_decorator(funcname);
        return 0;
    }
    if (!Decorator_Check(wrapper)) {
        PyErr_Format(PyExc_TypeError, "%s expected decorator type; got %s",
                     funcname, wrapper->ob_type->tp_name);
        return 0;
    }
    return 1;
}

static PyObject *
api_getmixin(PyObject *wrapper)
{
    /* Returns a borrowed reference. */
    if (wrapper == NULL)
        return missing_decorator("getmixin");
    if (check_decorator(wrapper, "getmixin"))
        return Decorator_GetMixin(wrapper);
    else
        return NULL;
}

static PyObject *
api_getmixinfactory(PyObject *wrapper)
{
    /* Returns a borrowed reference. */
    if (wrapper == NULL)
        return missing_decorator("getmixinfactory");
    if (check_decorator(wrapper, "getmixinfactory"))
        return Decorator_GetMixinFactory(wrapper);
    else
        return NULL;
}

static PyObject *
api_getnames(PyObject *wrapper)
{
    /* Returns a borrowed reference. */
    if (wrapper == NULL)
        return missing_decorator("getnames");
    if (check_decorator(wrapper, "getnames"))
        return Decorator_GetNames(wrapper);
    else
        return NULL;
}

static DecoratorInterface
decorator_capi = {
    api_check,
    api_create,
    api_getmixin,
    api_getmixinfactory,
    api_getnames,
};

static char
getmixin__doc__[] =
"getmixin(decorator) --> object\n"
"\n"
"Return the mixin object for the decorator. XXX continue from interface.";

static PyObject *
decorator_getmixin(PyObject *unused, PyObject *obj)
{
    PyObject *result = NULL;

    if (!check_decorator(obj, "getmixin"))
        return NULL;
    result = Decorator_GetMixin(obj);
    if (result == NULL)
        result = Py_None;
    Py_INCREF(result);
    return result;
}

static char
getmixincreate__doc__[] =
"getmixincreate(decorator) --> object\n"
"\n"
"Return the mixin object for the decorator. Creates it if it has not\n"
"already been created.";

static PyObject *
decorator_getmixincreate(PyObject *unused, PyObject *obj)
{
    PyObject *result = NULL;
    PyObject *temp;

    if (!check_decorator(obj, "getmixincreate"))
        return NULL;
    result = Decorator_GetMixin(obj);
    if (result == NULL) {
        temp = Decorator_GetMixinFactory(obj);
        if (temp == NULL) {
            PyErr_SetString(PyExc_TypeError,
                        "Cannot create mixin as there is no mixinfactory");
            return NULL;
        }
        result = PyObject_CallObject(temp, NULL);
        if (result == NULL)
            return NULL;
        ((DecoratorObject *)obj)->mixin = result;
    }
    Py_INCREF(result);
    return result;
}

static char
getmixinfactory__doc__[] =
"getmixinfactory(decorator) --> object\n"
"\n"
"Return the mixinfactory object for the decorator. XXX continue from interface.";

static PyObject *
decorator_getmixinfactory(PyObject *unused, PyObject *obj)
{
    PyObject *result = NULL;

    if (!check_decorator(obj, "getmixinfactory"))
        return NULL;
    result = Decorator_GetMixinFactory(obj);
    if (result == NULL)
        result = Py_None;
    Py_INCREF(result);
    return result;
}

static char
getnames__doc__[] =
"getnames(decorator) --> object\n"
"\n"
"Return the names tuple for the decorator. XXX continue from interface.";

static PyObject *
decorator_getnames(PyObject *unused, PyObject *obj)
{
    PyObject *result = NULL;

    if (!check_decorator(obj, "getnames"))
        return NULL;
    result = Decorator_GetNames(obj);
    Py_INCREF(result);
    return result;
}

static char
getnamesdict__doc__[] =
"getnamesdict(decorator) --> object\n"
"\n"
"Return the read-only names dict for the decorator. XXX continue from interface.";

static PyObject *
decorator_getnamesdict(PyObject *unused, PyObject *obj)
{
    if (!check_decorator(obj, "getnamesdict"))
        return NULL;
    return PyDictProxy_New(Decorator_GetNamesDict(obj));
}

static PyMethodDef
module_functions[] = {
    {"getmixin",          decorator_getmixin,          METH_O,
     getmixin__doc__},
    {"getmixincreate",    decorator_getmixincreate,    METH_O,
     getmixincreate__doc__},
    {"getmixinfactory",   decorator_getmixinfactory,   METH_O,
     getmixinfactory__doc__},
    {"getnames",          decorator_getnames,          METH_O,
     getnames__doc__},
    {"getnamesdict",      decorator_getnamesdict,      METH_O,
     getnamesdict__doc__},
    {NULL, NULL, 0, NULL}
};

static char
module___doc__[] =
"Context decorator objects.\n\
\n\
";

static PyObject *api_object = NULL;

void
initdecorator(void)
{
    PyObject *m;

    if (Proxy_Import() < 0)
        return;

    if (Wrapper_Import() < 0)
        return;

    m = Py_InitModule3("decorator", module_functions, module___doc__);
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

    DecoratorType.tp_base = &WrapperType;
    DecoratorType.tp_alloc = PyType_GenericAlloc;
    DecoratorType.tp_free = _PyObject_GC_Del;
    if (PyType_Ready(&DecoratorType) < 0)
        return;

    Py_INCREF(&DecoratorType);
    PyModule_AddObject(m, "Decorator", (PyObject *)&DecoratorType);

    if (api_object == NULL) {
        api_object = PyCObject_FromVoidPtr(&decorator_capi, NULL);
        if (api_object == NULL)
            return;
    }
    Py_INCREF(api_object);
    PyModule_AddObject(m, "_CAPI", api_object);

    if (empty_tuple == NULL)
        empty_tuple = PyTuple_New(0);
}

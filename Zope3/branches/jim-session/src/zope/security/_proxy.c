/*****************************************************************************
*
* Copyright (c) 2003, 2004 Zope Corporation and Contributors.
* All Rights Reserved.
*
* This software is subject to the provisions of the Zope Public License,
* Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
* THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
* WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
* WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
* FOR A PARTICULAR PURPOSE.
*
******************************************************************************
Security Proxy Implementation

$Id$
*/

#include <Python.h>
#include "proxy.h"

static PyObject *__class__str = 0, *__name__str = 0, *__module__str = 0;

typedef struct {
	ProxyObject proxy;
	PyObject *proxy_checker;
} SecurityProxy;

#undef Proxy_Check
#define Proxy_Check(proxy) \
	PyObject_TypeCheck(proxy, &SecurityProxyType)

#define Proxy_GetChecker(proxy) \
        (((SecurityProxy *)proxy)->proxy_checker)

/* Replace the "safe" version from the proxy.h API with a faster version. */
#undef Proxy_GetObject
#define Proxy_GetObject(o) \
        (((SecurityProxy *)o)->proxy.proxy_object)


static PyTypeObject SecurityProxyType;


/*
 * Machinery to call the checker.
 */

typedef PyObject *(*function1)(PyObject *);

static int
check(PyObject *checker, char *opname, PyObject *object)
{
	PyObject *checked;

	checked = PyObject_CallMethod(checker, "check", "(Os)",
				      object, opname);
	if (checked == NULL)
		return 0;
	Py_DECREF(checked);
	return 1;
}

static int
checkattr(PyObject *checker, char *check_method,
	  PyObject *object, PyObject *name)
{
	PyObject *checked;

	checked = PyObject_CallMethod(checker, check_method, "(OO)",
				      object, name);
	if (checked == NULL)
		return 0;
	Py_DECREF(checked);
	return 1;
}

static PyObject *
check1(SecurityProxy *self, char *opname, function1 operation)
{
	PyObject *result = NULL;
	PyObject *object = Proxy_GetObject(self);
	PyObject *checker = Proxy_GetChecker(self);

	if (check(checker, opname, object)) {
		result = operation(object);
		if (result != NULL)
			result = PyObject_CallMethod(checker, "proxy",
						     "(N)", result);
	}
	return result;
}

static PyObject *
check2(PyObject *self, PyObject *other,
       char *opname, char *ropname, binaryfunc operation)
{
	PyObject *result = NULL;
	PyObject *object;
	PyObject *checker;

	if (Proxy_Check(self)) {
		object = Proxy_GetObject(self);
		checker = Proxy_GetChecker(self);
		if (check(checker, opname, object))
			result = operation(object, other);
	}
	else if (Proxy_Check(other)) {
		object = Proxy_GetObject(other);
		checker = Proxy_GetChecker(other);
		if (check(checker, ropname, object))
			result = operation(self, object);
	}
	else {
		Py_INCREF(Py_NotImplemented);
		return Py_NotImplemented;
	}
	if (result != NULL)
		result = PyObject_CallMethod(checker, "proxy", "(N)", result);
	return result;
}

static PyObject *
check2i(SecurityProxy *self, PyObject *other,
	char *opname, binaryfunc operation)
{
	PyObject *result = NULL;
	PyObject *object = Proxy_GetObject(self);
	PyObject *checker = Proxy_GetChecker(self);

	if (check(checker, opname, object)) {
		result = operation(object, other);
		if (result == object) {
			/* If the operation was really carried out inplace,
			   don't create a new proxy, but use the old one. */
			Py_DECREF(object);
			Py_INCREF((PyObject *)self);
			result = (PyObject *)self;
		}
		else if (result != NULL)
			result = PyObject_CallMethod(checker, "proxy",
						     "(N)", result);
	}
	return result;
}

#define UNOP(NAME, CALL) \
	static PyObject *proxy_##NAME(PyObject *self) \
	{ return check1((SecurityProxy *)self, "__"#NAME"__", CALL); }

#define BINOP(NAME, CALL) \
	static PyObject *proxy_##NAME(PyObject *self, PyObject *other) \
	{ return check2(self, other, "__"#NAME"__", "__r"#NAME"__", CALL); }

#define INPLACE(NAME, CALL) \
	static PyObject *proxy_i##NAME(PyObject *self, PyObject *other) \
	{ return check2i((SecurityProxy *)self, other, "__i"#NAME"__", CALL); }


/*
 * Slot methods.
 */

static PyObject *
proxy_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	static char *kwlist[] = {"object", "checker", 0};
	SecurityProxy *self;
	PyObject *object;
	PyObject *checker;

	if (!PyArg_ParseTupleAndKeywords(args, kwds,
					 "OO:_Proxy.__new__", kwlist,
					 &object, &checker))
		return NULL;
	self = (SecurityProxy *)type->tp_alloc(type, 0);
	if (self == NULL)
		return NULL;
	Py_INCREF(object);
	Py_INCREF(checker);
	self->proxy.proxy_object = object;
	self->proxy_checker = checker;
	return (PyObject *)self;
}

/* This is needed to avoid calling the base class tp_init, which we
   don't need. */
static int
proxy_init(PyObject *self, PyObject *args, PyObject *kw)
{
	return 0;
}

static void
proxy_dealloc(PyObject *self)
{
	Py_DECREF(Proxy_GetChecker(self));
	SecurityProxyType.tp_base->tp_dealloc(self);
}

static int
proxy_traverse(PyObject *self, visitproc visit, void *arg)
{
	int err = visit(Proxy_GetObject(self), arg);
	if (err == 0)
		err = visit(Proxy_GetChecker(self), arg);
	return err;
}


/* Map rich comparison operators to their __xx__ namesakes */
static char *name_op[] = {
	"__lt__",
	"__le__",
	"__eq__",
	"__ne__",
	"__gt__",
	"__ge__",
};

static PyObject *
proxy_richcompare(PyObject* self, PyObject* other, int op)
{
	PyObject *result = NULL;
	PyObject *object = Proxy_GetObject(self);
	PyObject *checker = Proxy_GetChecker(self);

	if (check(checker, name_op[op], object)) {
		result = PyObject_RichCompare(object, other, op);
		if (result != NULL)
			result = PyObject_CallMethod(
				checker, "proxy", "(N)", result);
	}
	return result;
}

static PyObject *
proxy_iter(PyObject *self)
{
	PyObject *result = NULL;
	PyObject *object = Proxy_GetObject(self);
	PyObject *checker = Proxy_GetChecker(self);

	if (check(checker, "__iter__", object)) {
		result = PyObject_GetIter(object);
		if (result != NULL)
			result = PyObject_CallMethod(
				checker, "proxy", "(N)", result);
	}
	return result;
}

static PyObject *
proxy_iternext(PyObject *self)
{
	PyObject *result = NULL;
	PyObject *object = Proxy_GetObject(self);
	PyObject *checker = Proxy_GetChecker(self);

	if (check(checker, "next", object)) {
		result = PyIter_Next(object);
		if (result != NULL)
			result = PyObject_CallMethod(
				checker, "proxy", "(N)", result);
	}
	return result;
}

static PyObject *
proxy_getattro(PyObject *self, PyObject *name)
{
	PyObject *result = NULL;
	PyObject *object = Proxy_GetObject(self);
	PyObject *checker = Proxy_GetChecker(self);

	if (checkattr(checker, "check_getattr", object, name)) {
		result = PyObject_GetAttr(object, name);
		if (result != NULL)
			result = PyObject_CallMethod(
				checker, "proxy", "(N)", result);
	}
	return result;
}

static int
proxy_setattro(PyObject *self, PyObject *name, PyObject *value)
{
	PyObject *object = Proxy_GetObject(self);
	PyObject *checker = Proxy_GetChecker(self);

	if (checkattr(checker, "check_setattr", object, name))
		return PyObject_SetAttr(object, name, value);
	return -1;
}

static PyObject *
default_repr(PyObject *object)
{
	PyObject *klass, *name = 0, *module = 0, *result = 0;
	char *sname, *smodule;

	klass = PyObject_GetAttr(object, __class__str);
	if (klass == NULL)
		return NULL;

	name  = PyObject_GetAttr(klass, __name__str);
	if (name == NULL)
		goto err;
	sname = PyString_AsString(name);
	if (sname == NULL)
		goto err;

	module = PyObject_GetAttr(klass, __module__str);
	if (module != NULL) {
		smodule = PyString_AsString(module);
		if (smodule == NULL)
			goto err;
		result = PyString_FromFormat(
			"<security proxied %s.%s instance at %p>",
			smodule, sname, object);
	}
	else {
		PyErr_Clear();
		result = PyString_FromFormat(
			"<security proxied %s instance at %p>",
			sname, object);
	}

  err:
	Py_DECREF(klass);
	Py_XDECREF(name);
	Py_XDECREF(module);

	return result;
}

static PyObject *
proxy_str(PyObject *self)
{
	PyObject *result = NULL;
	PyObject *object = Proxy_GetObject(self);
	PyObject *checker = Proxy_GetChecker(self);

	if (check(checker, "__str__", object)) {
		result = PyObject_Str(object);
	}
	else {
		PyErr_Clear();
		result = default_repr(object);
	}
	return result;
}

static PyObject *
proxy_repr(PyObject *self)
{
	PyObject *result = NULL;
	PyObject *object = Proxy_GetObject(self);
	PyObject *checker = Proxy_GetChecker(self);

	if (check(checker, "__repr__", object)) {
		result = PyObject_Repr(object);
	}
	else {
		PyErr_Clear();
		result = default_repr(object);
	}
	return result;
}

static int
proxy_compare(PyObject *self, PyObject *other)
{
	PyObject *object = Proxy_GetObject(self);
	PyObject *checker = Proxy_GetChecker(self);

	if (check(checker, "__cmp__", object))
		return PyObject_Compare(object, other);
	return -1;
}

static long
proxy_hash(PyObject *self)
{
	PyObject *object = Proxy_GetObject(self);
	PyObject *checker = Proxy_GetChecker(self);

	if (check(checker, "__hash__", object))
		return PyObject_Hash(object);
	return -1;
}

static PyObject *
proxy_call(PyObject *self, PyObject *args, PyObject *kwds)
{
	PyObject *result = NULL;
	PyObject *object = Proxy_GetObject(self);
	PyObject *checker = Proxy_GetChecker(self);

	if (check(checker, "__call__", object)) {
		result = PyObject_Call(object, args, kwds);
		if (result != NULL)
			result = PyObject_CallMethod(
				checker, "proxy", "(N)", result);
	}
	return result;
}

/*
 * Number methods.
 */

static PyObject *
call_int(PyObject *self)
{
	PyNumberMethods *nb = self->ob_type->tp_as_number;
	if (nb == NULL || nb->nb_int == NULL) {
		PyErr_SetString(PyExc_TypeError,
				"object can't be converted to int");
		return NULL;
	}
	return nb->nb_int(self);
}

static PyObject *
call_long(PyObject *self)
{
	PyNumberMethods *nb = self->ob_type->tp_as_number;
	if (nb == NULL || nb->nb_long == NULL) {
		PyErr_SetString(PyExc_TypeError,
				"object can't be converted to long");
		return NULL;
	}
	return nb->nb_long(self);
}

static PyObject *
call_float(PyObject *self)
{
	PyNumberMethods *nb = self->ob_type->tp_as_number;
	if (nb == NULL || nb->nb_float== NULL) {
		PyErr_SetString(PyExc_TypeError,
				"object can't be converted to float");
		return NULL;
	}
	return nb->nb_float(self);
}

static PyObject *
call_oct(PyObject *self)
{
	PyNumberMethods *nb = self->ob_type->tp_as_number;
	if (nb == NULL || nb->nb_oct== NULL) {
		PyErr_SetString(PyExc_TypeError,
				"object can't be converted to oct");
		return NULL;
	}
	return nb->nb_oct(self);
}

static PyObject *
call_hex(PyObject *self)
{
	PyNumberMethods *nb = self->ob_type->tp_as_number;
	if (nb == NULL || nb->nb_hex == NULL) {
		PyErr_SetString(PyExc_TypeError,
				"object can't be converted to hex");
		return NULL;
	}
	return nb->nb_hex(self);
}

static PyObject *
call_ipow(PyObject *self, PyObject *other)
{
	/* PyNumber_InPlacePower has three args.  How silly. :-) */
	return PyNumber_InPlacePower(self, other, Py_None);
}

BINOP(add, PyNumber_Add)
BINOP(sub, PyNumber_Subtract)
BINOP(mul, PyNumber_Multiply)
BINOP(div, PyNumber_Divide)
BINOP(mod, PyNumber_Remainder)
BINOP(divmod, PyNumber_Divmod)

static PyObject *
proxy_pow(PyObject *self, PyObject *other, PyObject *modulus)
{
	PyObject *result = NULL;
	PyObject *object;
	PyObject *checker;

	if (Proxy_Check(self)) {
		object = Proxy_GetObject(self);
		checker = Proxy_GetChecker(self);
		if (check(checker, "__pow__", object))
			result = PyNumber_Power(object, other, modulus);
	}
	else if (Proxy_Check(other)) {
		object = Proxy_GetObject(other);
		checker = Proxy_GetChecker(other);
		if (check(checker, "__rpow__", object))
			result = PyNumber_Power(self, object, modulus);
	}
	else if (modulus != NULL && Proxy_Check(modulus)) {
		object = Proxy_GetObject(modulus);
		checker = Proxy_GetChecker(modulus);
		if (check(checker, "__3pow__", object))
			result = PyNumber_Power(self, other, modulus);
	}
	else {
		Py_INCREF(Py_NotImplemented);
		return Py_NotImplemented;
	}
	if (result != NULL)
		result = PyObject_CallMethod(checker, "proxy", "(N)", result);
	return result;
}

BINOP(lshift, PyNumber_Lshift)
BINOP(rshift, PyNumber_Rshift)
BINOP(and, PyNumber_And)
BINOP(xor, PyNumber_Xor)
BINOP(or, PyNumber_Or)

static int
proxy_coerce(PyObject **p_self, PyObject **p_other)
{
	PyObject *self = *p_self;
	PyObject *other = *p_other;
	PyObject *object;
	PyObject *checker;

	assert(Proxy_Check(self));
	object = Proxy_GetObject(self);
	checker = Proxy_GetChecker(self);

	if (check(checker, "__coerce__", object)) {
		PyObject *left = object;
		PyObject *right = other;
		int r;
		r = PyNumber_CoerceEx(&left, &right);
		if (r != 0)
			return r;
		/* Now left and right have been INCREF'ed.
		   Any new value that comes out is proxied;
		   any unchanged value is left unchanged. */
		if (left == object) {
			/* Keep the old proxy */
			Py_DECREF(left);
			Py_INCREF(self);
			left = self;
		}
		else {
			left = PyObject_CallMethod(checker, "proxy",
						   "(N)", left);
			if (left == NULL) {
				Py_DECREF(right);
				return -1;
			}
		}
		if (right != other) {
			right = PyObject_CallMethod(checker, "proxy",
						    "(N)", right);
			if (right == NULL) {
				Py_DECREF(left);
				return -1;
			}
		}
		*p_self = left;
		*p_other = right;
		return 0;
	}
	return -1;
}

UNOP(neg, PyNumber_Negative)
UNOP(pos, PyNumber_Positive)
UNOP(abs, PyNumber_Absolute)

static int
proxy_nonzero(PyObject *self)
{
	PyObject *object = Proxy_GetObject(self);
	PyObject *checker = Proxy_GetChecker(self);

	if (check(checker, "__nonzero__", object))
		return PyObject_IsTrue(object);
	return -1;
}

UNOP(invert, PyNumber_Invert)
UNOP(int, call_int)
UNOP(long, call_long)
UNOP(float, call_float)
UNOP(oct, call_oct)
UNOP(hex, call_hex)

INPLACE(add, PyNumber_InPlaceAdd)
INPLACE(sub, PyNumber_InPlaceSubtract)
INPLACE(mul, PyNumber_InPlaceMultiply)
INPLACE(div, PyNumber_InPlaceDivide)
INPLACE(mod, PyNumber_InPlaceRemainder)
INPLACE(pow, call_ipow)
INPLACE(lshift, PyNumber_InPlaceLshift)
INPLACE(rshift, PyNumber_InPlaceRshift)
INPLACE(and, PyNumber_InPlaceAnd)
INPLACE(xor, PyNumber_InPlaceXor)
INPLACE(or, PyNumber_InPlaceOr)

BINOP(floordiv, PyNumber_FloorDivide)
BINOP(truediv, PyNumber_TrueDivide)
INPLACE(floordiv, PyNumber_InPlaceFloorDivide)
INPLACE(truediv, PyNumber_InPlaceTrueDivide)

/*
 * Sequence methods.
 */

static int
proxy_length(PyObject *self)
{
	PyObject *object = Proxy_GetObject(self);
	PyObject *checker = Proxy_GetChecker(self);

	if (check(checker, "__len__", object))
		return PyObject_Length(object);
	return -1;
}

/* sq_item and sq_ass_item may be called by PySequece_{Get,Set}Item(). */
static PyObject *proxy_getitem(PyObject *, PyObject *);
static int proxy_setitem(PyObject *, PyObject *, PyObject *);

static PyObject *
proxy_igetitem(PyObject *self, int i)
{
	PyObject *key = PyInt_FromLong(i);
	PyObject *res = NULL;

	if (key != NULL) {
		res = proxy_getitem(self, key);
		Py_DECREF(key);
	}
	return res;
}


static int
proxy_isetitem(PyObject *self, int i, PyObject *value)
{
	PyObject *key = PyInt_FromLong(i);
	int res = -1;

	if (key != NULL) {
		res = proxy_setitem(self, key, value);
		Py_DECREF(key);
	}
	return res;
}

static PyObject *
proxy_slice(PyObject *self, int start, int end)
{
	PyObject *result = NULL;
	PyObject *object = Proxy_GetObject(self);
	PyObject *checker = Proxy_GetChecker(self);

	if (check(checker, "__getslice__", object)) {
		result = PySequence_GetSlice(object, start, end);
		if (result != NULL)
			result = PyObject_CallMethod(
				checker, "proxy", "(N)", result);
	}
	return result;
}

static int
proxy_ass_slice(PyObject *self, int i, int j, PyObject *value)
{
	PyObject *object = Proxy_GetObject(self);
	PyObject *checker = Proxy_GetChecker(self);

	if (check(checker, "__setslice__", object))
		return PySequence_SetSlice(object, i, j, value);
	return -1;
}

static int
proxy_contains(PyObject *self, PyObject *value)
{
	PyObject *object = Proxy_GetObject(self);
	PyObject *checker = Proxy_GetChecker(self);

	if (check(checker, "__contains__", object))
		return PySequence_Contains(object, value);
	return -1;
}

/*
 * Mapping methods.
 */

static PyObject *
proxy_getitem(PyObject *self, PyObject *key)
{
	PyObject *result = NULL;
	PyObject *object = Proxy_GetObject(self);
	PyObject *checker = Proxy_GetChecker(self);

	if (check(checker, "__getitem__", object)) {
		result = PyObject_GetItem(object, key);
		if (result != NULL)
			result = PyObject_CallMethod(
				checker, "proxy", "(N)", result);
	}
	return result;
}

static int
proxy_setitem(PyObject *self, PyObject *key, PyObject *value)
{
	PyObject *object = Proxy_GetObject(self);
	PyObject *checker = Proxy_GetChecker(self);

	if (value == NULL) {
		if (check(checker, "__delitem__", object))
			return PyObject_DelItem(object, key);
	}
	else {
		if (check(checker, "__setitem__", object))
			return PyObject_SetItem(object, key, value);
	}
	return -1;
}

/*
 * Normal methods.
 */

static PyNumberMethods
proxy_as_number = {
	proxy_add,				/* nb_add */
	proxy_sub,				/* nb_subtract */
	proxy_mul,				/* nb_multiply */
	proxy_div,				/* nb_divide */
	proxy_mod,				/* nb_remainder */
	proxy_divmod,				/* nb_divmod */
	proxy_pow,				/* nb_power */
	proxy_neg,				/* nb_negative */
	proxy_pos,				/* nb_positive */
	proxy_abs,				/* nb_absolute */
	proxy_nonzero,				/* nb_nonzero */
	proxy_invert,				/* nb_invert */
	proxy_lshift,				/* nb_lshift */
	proxy_rshift,				/* nb_rshift */
	proxy_and,				/* nb_and */
	proxy_xor,				/* nb_xor */
	proxy_or,				/* nb_or */
	proxy_coerce,				/* nb_coerce */
	proxy_int,				/* nb_int */
	proxy_long,				/* nb_long */
	proxy_float,				/* nb_float */
	proxy_oct,				/* nb_oct */
	proxy_hex,				/* nb_hex */

	/* Added in release 2.0 */
	/* These require the Py_TPFLAGS_HAVE_INPLACEOPS flag */
	proxy_iadd,				/* nb_inplace_add */
	proxy_isub,				/* nb_inplace_subtract */
	proxy_imul,				/* nb_inplace_multiply */
	proxy_idiv,				/* nb_inplace_divide */
	proxy_imod,				/* nb_inplace_remainder */
	(ternaryfunc)proxy_ipow,		/* nb_inplace_power */
	proxy_ilshift,				/* nb_inplace_lshift */
	proxy_irshift,				/* nb_inplace_rshift */
	proxy_iand,				/* nb_inplace_and */
	proxy_ixor,				/* nb_inplace_xor */
	proxy_ior,				/* nb_inplace_or */

	/* Added in release 2.2 */
	/* These require the Py_TPFLAGS_HAVE_CLASS flag */
	proxy_floordiv,				/* nb_floor_divide */
	proxy_truediv,				/* nb_true_divide */
	proxy_ifloordiv,			/* nb_inplace_floor_divide */
	proxy_itruediv,				/* nb_inplace_true_divide */
};

static PySequenceMethods
proxy_as_sequence = {
	proxy_length,				/* sq_length */
	0,					/* sq_concat */
	0,					/* sq_repeat */
	proxy_igetitem,				/* sq_item */
	proxy_slice,				/* sq_slice */
	proxy_isetitem,				/* sq_ass_item */
	proxy_ass_slice,				/* sq_ass_slice */
	proxy_contains,				/* sq_contains */
};

static PyMappingMethods
proxy_as_mapping = {
	proxy_length,				/* mp_length */
	proxy_getitem,				/* mp_subscript */
	proxy_setitem,				/* mp_ass_subscript */
};

static char proxy_doc[] = "\
Security proxy class.  Constructor: _Proxy(object, checker)\n\
where 'object' is an arbitrary object, and 'checker' is an object\n\
whose signature is described by the IChecker interface.\n\
A checker should have the following methods:\n\
  check(object, operation) # operation is e.g. '__add__' or '__hash__'\n\
  check_getattr(object, name)\n\
  check_setattr(object, name)\n\
  proxy(object)\n\
The check methods should raise an exception if the operation is\n\
disallowed.  The proxy method should return a proxy for the object\n\
if one is needed, otherwise the object itself.\n\
";

statichere PyTypeObject
SecurityProxyType = {
	PyObject_HEAD_INIT(NULL)
	0,
	"zope.security._proxy._Proxy",
	sizeof(SecurityProxy),
	0,
	proxy_dealloc,				/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	proxy_compare,				/* tp_compare */
	proxy_repr,				/* tp_repr */
	&proxy_as_number,			/* tp_as_number */
	&proxy_as_sequence,			/* tp_as_sequence */
	&proxy_as_mapping,			/* tp_as_mapping */
	proxy_hash,				/* tp_hash */
	proxy_call,				/* tp_call */
	proxy_str,				/* tp_str */
	proxy_getattro,				/* tp_getattro */
	proxy_setattro,				/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_CHECKTYPES |
		Py_TPFLAGS_HAVE_GC,		/* tp_flags */
	proxy_doc,				/* tp_doc */
	proxy_traverse,				/* tp_traverse */
	0,					/* tp_clear */
	proxy_richcompare,			/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	proxy_iter,				/* tp_iter */
	proxy_iternext,				/* tp_iternext */
	0,					/* tp_methods */
	0,					/* tp_members */
	0,					/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	proxy_init,				/* tp_init */
	0, /*PyType_GenericAlloc,*/		/* tp_alloc */
	proxy_new,				/* tp_new */
	0, /*_PyObject_GC_Del,*/		/* tp_free */
};

static PyObject *
module_getChecker(PyObject *self, PyObject *arg)
{
	PyObject *result;

	if (!Proxy_Check(arg)) {
		PyErr_SetString(PyExc_TypeError,
				"getChecker argument must be a _Proxy");
		return NULL;
	}
	result = Proxy_GetChecker(arg);
	Py_INCREF(result);
	return result;
}

static PyMethodDef
module_functions[] = {
	{"getChecker", module_getChecker, METH_O, "get checker from proxy"},
	{NULL}
};

static char
module___doc__[] = "Security proxy implementation.";

void
init_proxy(void)
{
	PyObject *m;

	if (Proxy_Import() < 0)
		return;

	__class__str = PyString_FromString("__class__");
	if (! __class__str) return;

	__name__str = PyString_FromString("__name__");
	if (! __name__str) return;

	__module__str = PyString_FromString("__module__");
	if (! __module__str) return;

	SecurityProxyType.ob_type = &PyType_Type;
	SecurityProxyType.tp_alloc = PyType_GenericAlloc;
	SecurityProxyType.tp_free = _PyObject_GC_Del;
	SecurityProxyType.tp_base = &ProxyType;
	if (PyType_Ready(&SecurityProxyType) < 0)
		return;

	m = Py_InitModule3("_proxy", module_functions, module___doc__);
	if (m == NULL)
		return;

	Py_INCREF(&SecurityProxyType);
	PyModule_AddObject(m, "_Proxy", (PyObject *)&SecurityProxyType);
}

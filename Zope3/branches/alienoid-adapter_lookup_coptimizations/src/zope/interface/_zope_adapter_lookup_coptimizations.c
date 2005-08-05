/*###########################################################################
 #
 # Copyright (c) 2005 Zope Corporation and Contributors.
 # All Rights Reserved.
 #
 # This software is subject to the provisions of the Zope Public License,
 # Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
 # THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
 # WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 # WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
 # FOR A PARTICULAR PURPOSE.
 #
 ############################################################################*/

#include "Python.h"
#include "structmember.h"
#include "_zope_interface_coptimizations.h"

#define TRUE 1
#define FALSE 0

typedef struct {
        PyObject_HEAD
        PyObject *_registry;
        PyObject *_surrogateClass;
        PyObject *_default;
        PyObject *_null;
        PyObject *_surrogates;
        PyObject *_remove;
} AdapterLookup;


static PyObject *strget, *strisOrExtends, *str__sro__, *strindex, *Null;
static PyObject *emptystr;

static int
AdapterLookup_init(AdapterLookup *self, PyObject *args, PyObject *keywds)
{
        PyObject *_registry = NULL, *_surrogates = NULL, *_remove = NULL;
        PyObject *tmp, *attr;

        if (!PyArg_ParseTuple(args, "OOO", &_registry, &_surrogates, &_remove))
                return -1;

        if (_registry) {
                tmp = self->_registry;
                Py_INCREF(_registry);
                self->_registry = _registry;
                Py_XDECREF(tmp);

                tmp = self->_surrogateClass;
                attr = PyObject_GetAttrString(_registry, "_surrogateClass");
                self->_surrogateClass = attr;
                Py_XDECREF(tmp);

                tmp = self->_default;
                attr = PyObject_GetAttrString(_registry, "_default");
                self->_default = attr;
                Py_XDECREF(tmp);

                tmp = self->_null;
                attr = PyObject_GetAttrString(_registry, "_null");
                self->_null = attr;
                Py_XDECREF(tmp);
        }
        if (_surrogates) {
                tmp = self->_surrogates;
                Py_XINCREF(_surrogates);
                self->_surrogates = _surrogates;
                Py_XDECREF(tmp);
        }
        if (_remove) {
                tmp = self->_remove;
                Py_XINCREF(_remove);
                self->_remove = _remove;
                Py_XDECREF(tmp);
        }
        return 0;
}


static int
AdapterLookup_traverse(AdapterLookup *self, visitproc visit, void *arg)
{
        Py_VISIT(self->_registry);
        Py_VISIT(self->_surrogateClass);
        Py_VISIT(self->_default);
        Py_VISIT(self->_null);
        Py_VISIT(self->_surrogates);
        Py_VISIT(self->_remove);
        return 0;
}

static int
AdapterLookup_clear(AdapterLookup *self)
{
        Py_CLEAR(self->_registry);
        Py_CLEAR(self->_surrogateClass);
        Py_CLEAR(self->_default);
        Py_CLEAR(self->_null);
        Py_CLEAR(self->_surrogates);
        Py_CLEAR(self->_remove);
        return 0;
}

static void
AdapterLookup_dealloc(AdapterLookup *self)
{
        AdapterLookup_clear(self);
        self->ob_type->tp_free((PyObject *)self);
}



static PyMemberDef AdapterLookup_members[] = {
        {"_registry", T_OBJECT_EX, offsetof(AdapterLookup, _registry), 0, ""},
        {"_surrogateClass", T_OBJECT_EX,
         offsetof(AdapterLookup, _surrogateClass), 0, ""},
        {"_default", T_OBJECT_EX, offsetof(AdapterLookup, _default), 0, ""},
        {"_null", T_OBJECT_EX, offsetof(AdapterLookup, _null), 0, ""},
        {"_surrogates", T_OBJECT_EX, offsetof(AdapterLookup, _surrogates),
         0, ""},
        {"_remove", T_OBJECT_EX, offsetof(AdapterLookup, _remove), 0, ""},
        {NULL}
};



static PyObject*
zip(PyObject *args)
{
	PyObject *ret;
	const int itemsize = PySequence_Length(args);
	int i;
	PyObject *itlist;  /* tuple of iterators */
	int len;	   /* guess at result length */

	if (itemsize == 0)
		return PyList_New(0);

	/* args must be a tuple */
	assert(PyTuple_Check(args));

	/* Guess at result length:  the shortest of the input lengths.
	   If some argument refuses to say, we refuse to guess too, lest
	   an argument like xrange(sys.maxint) lead us astray.*/
	len = -1;	/* unknown */
	for (i = 0; i < itemsize; ++i) {
		PyObject *item = PyTuple_GET_ITEM(args, i);
		int thislen = PyObject_Size(item);
		if (thislen < 0) {
			PyErr_Clear();
			len = -1;
			break;
		}
		else if (len < 0 || thislen < len)
			len = thislen;
	}

	/* allocate result list */
	if (len < 0)
		len = 10;	/* arbitrary */
	if ((ret = PyList_New(len)) == NULL)
		return NULL;

	/* obtain iterators */
	itlist = PyTuple_New(itemsize);
	if (itlist == NULL)
		goto Fail_ret;
	for (i = 0; i < itemsize; ++i) {
		PyObject *item = PyTuple_GET_ITEM(args, i);
		PyObject *it = PyObject_GetIter(item);
		if (it == NULL) {
			if (PyErr_ExceptionMatches(PyExc_TypeError))
				PyErr_Format(PyExc_TypeError,
				    "zip argument #%d must support iteration",
				    i+1);
			goto Fail_ret_itlist;
		}
		PyTuple_SET_ITEM(itlist, i, it);
	}

	/* build result into ret list */
	for (i = 0; ; ++i) {
		int j;
		PyObject *next = PyTuple_New(itemsize);
		if (!next)
			goto Fail_ret_itlist;

		for (j = 0; j < itemsize; j++) {
			PyObject *it = PyTuple_GET_ITEM(itlist, j);
			PyObject *item = PyIter_Next(it);
			if (!item) {
				if (PyErr_Occurred()) {
					Py_DECREF(ret);
					ret = NULL;
				}
				Py_DECREF(next);
				Py_DECREF(itlist);
				goto Done;
			}
			PyTuple_SET_ITEM(next, j, item);
		}

		if (i < len)
			PyList_SET_ITEM(ret, i, next);
		else {
			int status = PyList_Append(ret, next);
			Py_DECREF(next);
			++len;
			if (status < 0)
				goto Fail_ret_itlist;
		}
	}

Done:
	if (ret != NULL && i < len) {
		/* The list is too big. */
		if (PyList_SetSlice(ret, i, len, NULL) < 0)
			return NULL;
	}
	return ret;

Fail_ret_itlist:
	Py_DECREF(itlist);
Fail_ret:
	Py_DECREF(ret);
	return NULL;
}


static PyObject *
AdapterLookup_lookup(AdapterLookup *self, PyObject *args, PyObject *keywds)
{
        int i, j, k;
        PyObject *required, *provided;
        PyObject *name = NULL;
        PyObject *_default = Py_None;
        PyObject *surrogate, *byname, *value = NULL;


        static char *kwlist[] = {"required", "provided", "name", "default",
                                 NULL};
        if (!PyArg_ParseTupleAndKeywords(args, keywds, "OO|OO", kwlist,
                                         &required, &provided,
                                         &name, &_default))
                return NULL;

        const int order = PySequence_Length(required);

        if (name == NULL)
                name = PyString_FromString("");
        else
                Py_INCREF(name);

        if (order == 1) {
                /* Simple adapter */
                PyObject *req = PySequence_GetItem(required, 0);
                if (req == NULL)
                        goto on_error;
                surrogate = PyObject_CallMethodObjArgs((PyObject *)self,
                                                       strget, req, NULL);
                Py_DECREF(req);
                if (surrogate == NULL)
                        goto on_error;

                byname = PyObject_CallMethodObjArgs(surrogate, strget,
                                                    provided, NULL);
                Py_XDECREF(surrogate);
                if (byname == NULL)
                        goto on_error;

                if (byname != Py_None) {
                        value = PyDict_GetItem(byname, name);
                        if (value == NULL)
                                value = Py_None;
                } else
                        value = Py_None;

                Py_XDECREF(byname);

                if (value == Py_None) {
                        byname = PyObject_CallMethodObjArgs(self->_default,
                                                            strget,
                                                            provided, NULL);
                        if (byname == NULL)
                                goto on_error;

                        if (byname != Py_None) {
                                value = PyDict_GetItem(byname, name);
                                Py_XDECREF(byname);
                                if (value == NULL)
                                        value = _default;
                        } else {
                                Py_XDECREF(byname);
                                Py_XDECREF(name);
                                Py_INCREF(_default);
                                return _default;
                        }
                }

                Py_XDECREF(name);
                Py_INCREF(value);
                return value;

        on_error:
                Py_XDECREF(name);
                return NULL;

        } else if (!order) {
                /* null adapter */
                byname = PyObject_CallMethodObjArgs(self->_null,
                                                    strget,
                                                    provided, NULL);
                if (byname == NULL) {
                        Py_XDECREF(name);
                        return NULL;
                }

                if (byname != Py_None) {
                        value = PyDict_GetItem(byname, name);
                        Py_XDECREF(byname);
                        if (value == NULL)
                                value = _default;
                        Py_XDECREF(name);
                        Py_XINCREF(value);
                        return value;
                }

                Py_XDECREF(byname);
                Py_XDECREF(name);
                Py_INCREF(_default);
                return _default;
        }

        /* Multi adapter */
        PyObject *with, *tmp;

        with = PySequence_GetSlice(required, 1, order); /* new reference */
        if (with == NULL)
                goto fail_with;
        PyObject *key = Py_BuildValue("Oi", provided, order);

        PyObject *req = PySequence_GetItem(required, 0);
        if (req == NULL)
                goto fail_req;

        surrogate = PyObject_CallMethodObjArgs((PyObject *)self, strget,
                                               req, NULL);
        Py_DECREF(req);
        if (surrogate == NULL)
                goto fail_req;

        PyObject *surrogates = Py_BuildValue("OO", surrogate, self->_default);
        Py_XDECREF(surrogate);

        int surrogates_len = PyTuple_GET_SIZE(surrogates);

        /* for surrogate in self.get(required[0]), self._default: */
        for (i = 0; i < surrogates_len; i++) {
                surrogate = PyTuple_GET_ITEM(surrogates, i);
                byname = PyObject_CallMethodObjArgs(surrogate, strget,
                                                    key, NULL);
                if (byname == NULL) {
                        Py_DECREF(surrogates);
                        goto fail_req;
                }

                if (byname == Py_None) {
                        Py_DECREF(byname);
                        continue;
                }

                PyObject *bywith = PyDict_GetItem(byname, name);
                Py_DECREF(byname);
                if (bywith == NULL)
                        continue;

                PyObject *best = NULL;
                PyObject *rwith, *value;

                /* for rwith, value in bywith: */
                int bywith_length = PySequence_Length(bywith);
                for (j = 0; j < bywith_length; j++) {
                        tmp = PySequence_GetItem(bywith, j);
                        if (!PyArg_ParseTuple(tmp, "OO", &rwith, &value)) {
                                Py_DECREF(tmp);
                                Py_DECREF(surrogates);
                                goto fail_req;
                        }
                        Py_DECREF(tmp);

                        PyObject *rank = PyList_New(0);

                        tmp = Py_BuildValue("OO", rwith, with);
                        PyObject *seq = zip(tmp);
                        Py_DECREF(tmp);

                        int seq_length = PySequence_Length(seq);

                        /* for rspec, spec in zip(rwith, with): */
                        for (k = 0; k < seq_length; k++) {
                                PyObject *spec, *rspec;

                                tmp = PyList_GET_ITEM(seq, k);
                                rspec = PyTuple_GET_ITEM(tmp, 0);
                                spec = PyTuple_GET_ITEM(tmp, 1);

                                PyObject *res;
                                res = PyObject_CallMethodObjArgs(spec,
                                                                 strisOrExtends,
                                                                 rspec,
                                                                 NULL);
                                if (res == NULL) {
                                        Py_DECREF(rank);
                                        Py_XDECREF(seq);
                                        goto fail_req;
                                }
                                if (PyObject_Not(res)) {
                                        Py_DECREF(res);
                                        goto done;
                                }
                                Py_DECREF(res);

                                PyObject *sro = PyObject_GetAttr(spec,
                                                                 str__sro__);
                                PyObject *sro_list = PySequence_List(sro);

                                Py_XDECREF(sro);

                                PyObject *index;
                                index = PyObject_CallMethodObjArgs(sro_list,
                                                                   strindex,
                                                                   rspec,
                                                                   NULL);
                                Py_XDECREF(sro_list);
                                if (index == NULL) {
                                        Py_DECREF(rank);
                                        Py_XDECREF(seq);
                                        goto fail_req;
                                }

                                if (PyList_Append(rank, index) < 0) {
                                        Py_XDECREF(index);
                                        Py_DECREF(rank);
                                        Py_XDECREF(seq);
                                        goto fail_req;
                                }

                                Py_XDECREF(index);
                        }

                        /* rank = tuple(rank)
                           if best is None or rank < best[0]:
                               best = rank, value
                        */
                        tmp = rank;
                        rank = PySequence_Tuple(rank);
                        Py_XDECREF(tmp);

                        if (best == NULL ||
                            PyObject_Compare(rank,
                                             PyTuple_GET_ITEM(best, 0)) < 0) {
                                Py_XDECREF(best);
                                best = Py_BuildValue("OO", rank, value);
                        }
                done:
                        Py_XDECREF(seq);
                        Py_XDECREF(rank);
                }
                /* if best:
                       return best[1]
                */
                if (best != NULL) {
                        tmp = PyTuple_GET_ITEM(best, 1);
                        Py_XINCREF(tmp);
                        Py_XDECREF(best);
                        _default = tmp;
                        goto finish;
                }
        }

finish:
        Py_XDECREF(surrogates);
        Py_XDECREF(key);
        Py_XDECREF(with);
        Py_XDECREF(name);
        if (_default == NULL) {
                Py_INCREF(Py_None);
                return Py_None;
        }

        return _default;

fail_req:
        Py_DECREF(with);
fail_with:
        Py_XDECREF(name);
        return NULL;
}

static PyObject *
AdapterLookup_lookup1(AdapterLookup *self, PyObject *args, PyObject *keywds)
{
        PyObject *required, *provided;
        PyObject *name = emptystr;
        PyObject *_default = Py_None;
        PyObject *required_list;
        PyObject *res;
        PyObject *param_args, *kw;

        static char *kwlist[] = {"required", "provided", "name", "default",
                                 NULL};
        if (!PyArg_ParseTupleAndKeywords(args, keywds, "OO|OO", kwlist,
                                         &required, &provided,
                                         &name, &_default))
                return NULL;

        param_args = Py_BuildValue("[O]OOO", required, provided,
                                   name, _default);

        res = AdapterLookup_lookup(self, param_args, NULL);
        Py_DECREF(param_args);

        return res;
}

static PyObject *
AdapterLookup_adapter_hook(AdapterLookup *self, PyObject *args,
                           PyObject *keywds)
{
        PyObject *interface;
        PyObject *object;
        PyObject *name = emptystr;
        PyObject *_default = Py_None;

        static char *kwlist[] = {"interface", "object", "name", "default",
                                 NULL};

        if (!PyArg_ParseTupleAndKeywords(args, keywds, "OO|OO", kwlist,
                                         &interface, &object,
                                         &name, &_default))
                return NULL;

        /* factory = self.lookup1(providedBy(object), interface, name) */
        PyObject *required = providedBy(NULL, object);
        PyObject *lookup_args = Py_BuildValue("OOO", required, interface,
                                              name);
        Py_DECREF(required);

        PyObject *factory = AdapterLookup_lookup1(self, lookup_args, NULL);
        Py_DECREF(lookup_args);

        /*
           if factory is not None:
               adapter = factory(object)
               if adapter is not None:
                   return adapter
           return default
        */
        if (factory != Py_None) {
                PyObject *params = Py_BuildValue("(O)", object);
                PyObject *adapter = PyObject_CallObject(factory, params);
                Py_DECREF(params);
                if (adapter == NULL) {
                        Py_DECREF(factory);
                        return NULL;
                }
                if (adapter != Py_None) {
                        Py_DECREF(factory);
                        return adapter;
                }
        }
        Py_XDECREF(factory);
        if (_default == Py_None) {
                Py_INCREF(Py_None);
                return Py_None;
        }
        Py_INCREF(_default);
        return _default;
}

static PyObject *
AdapterLookup_queryAdapter(AdapterLookup *self, PyObject *args,
                           PyObject *keywds)
{
        PyObject *interface;
        PyObject *object;
        PyObject *name = emptystr;
        PyObject *_default = Py_None;

        static char *kwlist[] = {"object", "interface", "name", "default",
                                 NULL};
        if (!PyArg_ParseTupleAndKeywords(args, keywds, "OO|OO", kwlist,
                                         &object, &interface,
                                         &name, &_default))
                return NULL;

        PyObject *params = Py_BuildValue("OOOO", interface, object,
                                         name, _default);
        PyObject *result =  AdapterLookup_adapter_hook(self, params, NULL);
        Py_DECREF(params);

        if (result == NULL)
                return NULL;

        return result;
}

static PyObject *
AdapterLookup_subscriptions(AdapterLookup* self, PyObject *args)
{
        int i, j, k;
        PyObject *required, *provided;
        PyObject *surrogate, *result, *tmp;

        if (!PyArg_ParseTuple(args, "OO", &required, &provided))
                return NULL;

        if (provided == Py_None)
                provided = Null;

        const int order = PySequence_Length(required);


        if (order == 1) {
                /* Simple subscriptions */
                PyObject *req = PySequence_GetItem(required, 0);
                if (req == NULL)
                        return NULL;
                surrogate = PyObject_CallMethodObjArgs((PyObject *)self,
                                                       strget, req, NULL);
                Py_DECREF(req);

                PyObject *params = Py_BuildValue("sO", "s", provided);

                /*
                   result = s.get(('s', provided))
                   if result:
                       result = list(result)
                   else:
                       result = []
                */
                result = PyObject_CallMethodObjArgs(surrogate, strget,
                                                    params, NULL);
                Py_DECREF(surrogate);

                if (result == NULL) {
                        Py_DECREF(params);
                        return NULL;
                }

                if (result != Py_None) {
                        tmp = result;
                        result = PySequence_List(result);
                        Py_XDECREF(tmp);
                } else {
                        Py_DECREF(result);
                        result = PyList_New(0);
                }

                PyObject *_default;
                _default = PyObject_CallMethodObjArgs(self->_default,
                                                      strget,
                                                      params, NULL);
                Py_DECREF(params);
                if (_default == NULL) {
                        Py_DECREF(result);
                }

                /*
                  if default:
                      result.extend(default)

                  return result
                */
                if (_default != Py_None) {
                        int len = PyList_GET_SIZE(result);
                        int status;
                        status = PyList_SetSlice(result, len, len, _default);

                        if (status < 0) {
                                Py_DECREF(_default);
                                Py_DECREF(result);
                                return NULL;
                        }
                }
                Py_DECREF(_default);
                return result;

        } else if (!order) {
                /*
                  result = self._null.get(('s', provided))
                  if result:
                      return list(result)
                  else:
                      return []
                */
                PyObject *params = Py_BuildValue("sO", "s", provided);

                result = PyObject_CallMethodObjArgs(self->_null,
                                                    strget,
                                                    params, NULL);
                Py_DECREF(params);

                if (result == NULL)
                        return NULL;

                if (result != Py_None) {
                        tmp = result;
                        result = PySequence_List(result);
                        Py_XDECREF(tmp);
                        return result;
                }
                Py_DECREF(result);
                return PyList_New(0);
        }

        /* Multi */
        PyObject *surrogates = NULL;
        PyObject *with = PySequence_GetSlice(required, 1, order);
        if (with == NULL)
                return NULL;

        PyObject *key = Py_BuildValue("sOi", "s", provided, order);

        PyObject *req = PySequence_GetItem(required, 0);
        if (req == NULL)
                goto on_error;

        surrogate = PyObject_CallMethodObjArgs((PyObject *)self,
                                               strget, req, NULL);
        Py_DECREF(req);
        if (surrogate == NULL)
                goto on_error;

        surrogates = Py_BuildValue("OO", surrogate, self->_default);
        Py_XDECREF(surrogate);
        int surrogates_len = PyTuple_GET_SIZE(surrogates);

        result = PyList_New(0);

        /* for surrogate in self.get(required[0]), self._default: */
        for (i = 0; i < surrogates_len; i++) {
                surrogate = PySequence_GetItem(surrogates, i);
                PyObject *bywith = PyObject_CallMethodObjArgs(surrogate,
                                                              strget,
                                                              key, NULL);
                Py_DECREF(surrogate);
                if (bywith == NULL)
                        goto on_error;

                if (PyObject_Not(bywith)) {
                        Py_DECREF(bywith);
                        continue;
                }

                PyObject *rwith, *values;

                /* for rwith, values in bywith: */
                int bywith_length = PySequence_Length(bywith);
                for (j = 0; j < bywith_length; j++) {
                        tmp = PySequence_GetItem(bywith, j);
                        if (!PyArg_ParseTuple(tmp, "OO", &rwith, &values)) {
                                Py_XDECREF(tmp);
                                Py_XDECREF(bywith);
                                goto on_error;
                        }
                        Py_DECREF(tmp);

                        tmp = Py_BuildValue("OO", rwith, with);
                        PyObject *seq = zip(tmp);
                        Py_DECREF(tmp);

                        int seq_length = PySequence_Length(seq);

                        int spec_extends = TRUE;
                        /* for rspec, spec in zip(rwith, with): */
                        for (k = 0; k < seq_length; k++) {
                                PyObject *spec, *rspec;

                                tmp = PyList_GET_ITEM(seq, k);

                                rspec = PyTuple_GET_ITEM(tmp, 0);
                                spec = PyTuple_GET_ITEM(tmp, 1);

                                PyObject *res;
                                res = PyObject_CallMethodObjArgs(spec,
                                                                 strisOrExtends,
                                                                 rspec,
                                                                 NULL);

                                if (res == NULL) {
                                        Py_XDECREF(seq);
                                        Py_XDECREF(bywith);
                                        goto on_error;
                                }
                                if (PyObject_Not(res)) {
                                        spec_extends = FALSE;
                                        Py_DECREF(res);
                                        break;
                                }
                                Py_DECREF(res);
                        }
                        if (spec_extends) {
                                /* result.extend(values) */
                                int len = PyList_GET_SIZE(result);
                                if (PyList_SetSlice(result, len, len,
                                                    values) < 0)
                                        goto on_error;
                        }
                        Py_XDECREF(seq);
                }
                Py_XDECREF(bywith);
        }

        Py_XDECREF(surrogates);
        Py_XDECREF(key);
        Py_XDECREF(with);
        return result;

on_error:
        Py_DECREF(result);
        Py_XDECREF(surrogates);
        Py_XDECREF(key);
        Py_XDECREF(with);
        return NULL;
}


static PyObject *
AdapterLookup_queryMultiAdapter(AdapterLookup* self, PyObject *args,
                                PyObject *keywds)
{
        PyObject *interface;
        PyObject *objects;
        PyObject *name = NULL;
        PyObject *_default = Py_None;
        PyObject *tmp;
        int nobjects;
        int i;

        static char *kwlist[] = {"object", "interface", "name", "default",
                                 NULL};
        if (!PyArg_ParseTupleAndKeywords(args, keywds, "OO|OO", kwlist,
                                         &objects, &interface,
                                         &name, &_default))
                return NULL;

        nobjects = PySequence_Length(objects);

        if (name == NULL)
                name = PyString_FromString("");
        else
                Py_INCREF(name);

        /* factory = self.lookup(map(providedBy, objects), interface, name) */
        PyObject *required = PyList_New(nobjects);
        for (i = 0; i < nobjects; i++) {
                tmp = PySequence_GetItem(objects, i);
                PyList_SetItem(required, i, providedBy(NULL, tmp));
                Py_DECREF(tmp);
        }

        PyObject *lookup_args = Py_BuildValue("OO", required, interface);
        PyObject *kw = Py_BuildValue("{s:O}", "name", name);
        Py_DECREF(required);

        PyObject *factory = AdapterLookup_lookup(self, lookup_args, kw);
        Py_DECREF(kw);
        Py_DECREF(lookup_args);

        /*
          if factory is not None:
              return factory(*objects)
          return default
        */
        if (factory != Py_None) {
                objects = PySequence_Tuple(objects);
                PyObject *result = PyObject_CallObject(factory, objects);
                Py_DECREF(objects);
                Py_DECREF(factory);
                Py_XDECREF(name);
                return result;
        }

        Py_DECREF(factory);
        Py_XDECREF(name);

        Py_INCREF(_default);
        return _default;
}

static PyObject *
AdapterLookup_subscribers(AdapterLookup *self, PyObject *args)
{
        PyObject *interface;
        PyObject *objects;
        PyObject *tmp;
        int nobjects;
        int i;

        if (!PyArg_ParseTuple(args, "OO", &objects, &interface))
                return NULL;

        nobjects = PySequence_Length(objects);

        PyObject *required = PyList_New(nobjects);
        for (i = 0; i < nobjects; i++) {
                tmp = PySequence_GetItem(objects, i);
                PyList_SetItem(required, i, providedBy(NULL, tmp));
                Py_DECREF(tmp);
        }

        PyObject *subs_args = Py_BuildValue("OO", required, interface);
        Py_DECREF(required);

        PyObject *subscriptions = AdapterLookup_subscriptions(self, subs_args);
        Py_DECREF(subs_args);

        if (subscriptions == NULL)
                return NULL;

        PyObject *it = PyObject_GetIter(subscriptions);
        PyObject *item;

        if (it == NULL)
                goto on_error;

        /*
          subscribers = [subscription(*objects)
                         for subscription in subscriptions]
        */
        PyObject *subscribers = PyList_New(0);
        while (item = PyIter_Next(it)) {
                /* make sure we pass tuple as argument list to method call */
                PyObject *objects_tuple = PySequence_Tuple(objects);
                tmp = PyObject_CallObject(item, objects_tuple);
                Py_DECREF(objects_tuple);
                if (tmp == NULL) {
                        Py_DECREF(item);
                        Py_DECREF(it);
                        goto on_error;
                }
                PyList_Append(subscribers, tmp);
                Py_DECREF(tmp);
                Py_DECREF(item);
        }

        Py_DECREF(it);

        if (PyErr_Occurred()) {
                Py_XDECREF(subscribers);
                goto on_error;
        }

        it = PyObject_GetIter(subscribers);
        if (it == NULL) {
                Py_XDECREF(subscribers);
                goto on_error;
        }

        PyObject *result = PyList_New(0);
        while (item = PyIter_Next(it)) {
                if (item != Py_None)
                        PyList_Append(result, item);
                Py_DECREF(item);
        }

        Py_DECREF(it);

        if (PyErr_Occurred()) {
                Py_XDECREF(result);
                Py_XDECREF(subscribers);
                goto on_error;
        }

        Py_XDECREF(subscriptions);
        return result;

on_error:
        Py_XDECREF(subscriptions);
        return NULL;

}

static PyObject *
AdapterLookup_get(AdapterLookup *self, PyObject *args)
{
        PyObject *decl = NULL, *ref, *surrogate, *init_args;

        if (!PyArg_ParseTuple(args, "O", &decl))
                return NULL;

        if (decl == Py_None) {
                Py_INCREF(self->_default);
                return self->_default;
        }

        ref = PyObject_CallMethod(decl, "weakref", "O", self->_remove);

        if (ref == NULL)
                return NULL;

        surrogate = PyDict_GetItem(self->_surrogates, ref);
        /* no ref key in dictionary */
        if (surrogate == NULL || surrogate == Py_None) {
                init_args = Py_BuildValue("OO", decl, self->_registry);

                surrogate = PyObject_CallObject(self->_surrogateClass,
                                                init_args);
                if (surrogate == NULL) {
                        Py_DECREF(init_args);
                        Py_XDECREF(ref);
                        return NULL;
                }
                PyDict_SetItem(self->_surrogates, ref, surrogate);

                Py_DECREF(init_args);
                Py_XDECREF(ref);
                return surrogate;
        }

        Py_XDECREF(ref);
        Py_INCREF(surrogate);
        return surrogate;
}

static PyMethodDef AdapterLookup_methods[] = {
        {"lookup", (PyCFunction)AdapterLookup_lookup,
         METH_VARARGS | METH_KEYWORDS, ""},
        {"lookup1", (PyCFunction)AdapterLookup_lookup1,
         METH_VARARGS | METH_KEYWORDS, ""},
        {"adapter_hook", (PyCFunction)AdapterLookup_adapter_hook,
         METH_VARARGS | METH_KEYWORDS, ""},
        {"queryAdapter", (PyCFunction)AdapterLookup_queryAdapter,
         METH_VARARGS | METH_KEYWORDS, ""},
        {"subscriptions", (PyCFunction)AdapterLookup_subscriptions,
         METH_VARARGS, ""},
        {"queryMultiAdapter", (PyCFunction)AdapterLookup_queryMultiAdapter,
         METH_VARARGS | METH_KEYWORDS, ""},
        {"subscribers", (PyCFunction)AdapterLookup_subscribers,
         METH_VARARGS, ""},
        {"get", (PyCFunction)AdapterLookup_get, METH_VARARGS, ""},
        {NULL} /* Sentinel */
};


static PyTypeObject AdapterLookupType = {
	PyObject_HEAD_INIT(NULL)
	/* ob_size           */ 0,
	/* tp_name           */ "_adapter_lookup_coptimizations."
                                "AdapterLookup",
	/* tp_basicsize      */ sizeof(AdapterLookup),
	/* tp_itemsize       */ 0,
	/* tp_dealloc        */ (destructor)AdapterLookup_dealloc,
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
        /* tp_flags          */ Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
        "C class for AdapterLookup",
        /* tp_traverse       */ (traverseproc)AdapterLookup_traverse,
        /* tp_clear          */ (inquiry)AdapterLookup_clear,
        /* tp_richcompare    */ (richcmpfunc)0,
        /* tp_weaklistoffset */ (long)0,
        /* tp_iter           */ (getiterfunc)0,
        /* tp_iternext       */ (iternextfunc)0,
        /* tp_methods        */ AdapterLookup_methods,
        /* tp_members        */ AdapterLookup_members,
        /* tp_getset         */ 0,
        /* tp_base           */ 0,
        /* tp_dict           */ 0, /* internal use */
        /* tp_descr_get      */ (descrgetfunc)0,
        /* tp_descr_set      */ (descrsetfunc)0,
        /* tp_dictoffset     */ 0,
        /* tp_init           */ (initproc)AdapterLookup_init,
};


static struct PyMethodDef m_methods[] = {
        {NULL} /* Sentinel */
};

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
init_zope_adapter_lookup_coptimizations(void)
{
        PyObject *m;

#define DEFINE_STRING(s) \
if (!(str##s = PyString_FromString(#s))) return
        DEFINE_STRING(get);
        DEFINE_STRING(isOrExtends);
        DEFINE_STRING(__sro__);
        DEFINE_STRING(index);
#undef DEFINE_STRING

        emptystr = PyString_FromString("");

        /* Initialize types: */
        AdapterLookupType.tp_new = PyType_GenericNew;
        if (PyType_Ready(&AdapterLookupType) < 0)
                return;

        /* Create the module and add the functions */
        m = Py_InitModule3("_zope_adapter_lookup_coptimizations", m_methods,
                           "C optimizations for "
                           "zope.interface.adapter.AdapterLookup\n\n"
                           "$Id$");
        if (m == NULL)
                return;

        if (import_zope_interface_coptimizations() < 0)
                return;

        PyObject *adapter = PyImport_ImportModule("zope.interface.adapter");
        if (adapter == NULL)
                return;

        Null = PyObject_GetAttrString(adapter, "Null");
        Py_DECREF(adapter);

        if (Null == NULL)
                return;

        /* Add types: */
        Py_INCREF(&AdapterLookupType);
        if (PyModule_AddObject(m, "AdapterLookup",
                               (PyObject *)&AdapterLookupType) < 0)
                return;
}

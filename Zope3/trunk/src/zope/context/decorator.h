/* Decorator objects.
 *
 * This is intended for use with Python 2.2.
 *
 * Created by Steve Alexander and Marius Gedminas, 2003-May-7.
 */

#ifndef _decorator_H_
#define _decorator_H_

#ifndef _wrapper_H_
#include "zope/proxy/context/wrapper.h"
#endif

typedef struct {
    WrapperObject wrapperobject;
    PyObject *mixin_factory;
    PyObject *mixin;
    PyObject *names;
    PyObject *names_dict;
    PyObject *inner;
} DecoratorObject;

typedef struct {
    int (*check)(PyObject *obj);
    PyObject *(*create)(PyObject *object, PyObject *context,
        PyObject *mixin_factory, PyObject *names, PyObject *attrdict,
        PyObject *inner);
    PyObject *(*getmixin)(PyObject *wrapper);
    PyObject *(*getmixinfactory)(PyObject *wrapper);
    PyObject *(*getnames)(PyObject *wrapper);
    PyObject *(*getinner)(PyObject *wrapper);
} DecoratorInterface;


#ifndef DECORATOR_MODULE

/* These are only defined in the public interface, and are not
 * available within the module implementation.  There we use the
 * classic Python/C API only.
 */

static DecoratorInterface *_decorator_api = NULL;

static int
Decorator_Import(void)
{
    if (_decorator_api == NULL) {
        PyObject *m = PyImport_ImportModule("zope.proxy.context.decorator");
        if (m != NULL) {
            PyObject *tmp = PyObject_GetAttrString(m, "_CAPI");
            if (tmp != NULL) {
                if (PyCObject_Check(tmp))
                    _decorator_api = (DecoratorInterface *)
                        PyCObject_AsVoidPtr(tmp);
                Py_DECREF(tmp);
            }
        }
    }
    return (_decorator_api == NULL) ? -1 : 0;
}

#define Decorator_Check(obj)                                              \
        (_decorator_api->check((obj)))
#define Decorator_New(object, context, mixin_factory, names, attrdict,    \
                      inner)                                              \
        (_decorator_api->create((object), (context), (mixin_factory),     \
                                (names), (attrdict), (inner)))
#define Decorator_GetMixin(wrapper)                                       \
        (_decorator_api->getmixin((wrapper)))
#define Decorator_GetMixinFactory(wrapper)                                \
        (_decorator_api->getmixinfactory((wrapper)))
#define Decorator_GetNames(wrapper)                                       \
        (_decorator_api->getnames((wrapper)))
#define Decorator_GetInner(wrapper)                                       \
        (_decorator_api->getinner((wrapper)))

#endif

#endif

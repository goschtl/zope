/* Context Wrapper object; see "BasicContextWrapper" in the Zope 3 wiki:
 * http://dev.zope.org/Wikis/DevSite/Projects/ComponentArchitecture/
 *
 * This is intended for use with Python 2.2.
 *
 * Created by Fred Drake, 2001-Nov-09.
 */

#ifndef _wrapper_H_
#define _wrapper_H_

#ifndef _proxy_H_
#include "zope/proxy/proxy.h"
#endif

typedef struct {
    PyObject_HEAD
    PyObject *proxy_object;
    PyObject *wrap_context;
    PyObject *wrap_dict;
} WrapperObject;

typedef struct {
    PyTypeObject *wrappertype;
    PyTypeObject *contextdescriptortype;
    PyTypeObject *contextawaretype;
    int (*check)(PyObject *obj);
    PyObject *(*create)(PyObject *object, PyObject *context);
    PyObject *(*getobject)(PyObject *wrapper);
    PyObject *(*getbaseobject)(PyObject *wrapper);
    PyObject *(*getcontext)(PyObject *wrapper);
    PyObject *(*getinnercontext)(PyObject *wrapper);
    PyObject *(*getinnerwrapper)(PyObject *wrapper);
    PyObject *(*getdict)(PyObject *wrapper);
    PyObject *(*getdictcreate)(PyObject *wrapper);
    int (*setobject)(PyObject *wrapper, PyObject *object);
    int (*setcontext)(PyObject *wrapper, PyObject *context);
} WrapperInterface;


#ifndef WRAPPER_MODULE

/* These are only defined in the public interface, and are not
 * available within the module implementation.  There we use the
 * classic Python/C API only.
 */

static WrapperInterface *_wrapper_api = NULL;

static int
Wrapper_Import(void)
{
    if (_wrapper_api == NULL) {
        PyObject *m = PyImport_ImportModule("zope.proxy.context.wrapper");
        if (m != NULL) {
            PyObject *tmp = PyObject_GetAttrString(m, "_CAPI");
            if (tmp != NULL) {
                if (PyCObject_Check(tmp))
                    _wrapper_api = (WrapperInterface *)
                        PyCObject_AsVoidPtr(tmp);
                Py_DECREF(tmp);
            }
        }
    }
    return (_wrapper_api == NULL) ? -1 : 0;
}

#define WrapperType                       \
        (_wrapper_api->wrappertype)
#define ContextDescriptorType             \
        (_wrapper_api->contextdescriptortype)
#define ContextAwareType                  \
        (_wrapper_api->contextawaretype)
#define Wrapper_Check(obj)                   \
        (_wrapper_api->check((obj)))
#define Wrapper_New(object, context)         \
        (_wrapper_api->create((object), (context)))
#define Wrapper_GetObject(wrapper)           \
        (_wrapper_api->getobject((wrapper)))
#define Wrapper_GetBaseObject(wrapper)           \
        (_wrapper_api->getbaseobject((wrapper)))
#define Wrapper_GetContext(wrapper)          \
        (_wrapper_api->getcontext((wrapper)))
#define Wrapper_GetInnerContext(wrapper)          \
        (_wrapper_api->getinnercontext((wrapper)))
#define Wrapper_GetInnerWrapper(wrapper)          \
        (_wrapper_api->getinnerwrapper((wrapper)))
#define Wrapper_GetDict(wrapper)             \
        (_wrapper_api->getdict((wrapper)))
#define Wrapper_GetDictCreate(wrapper)       \
        (_wrapper_api->getdictcreate((wrapper)))
#define Wrapper_SetObject(wrapper, object)   \
        (_wrapper_api->setobject((wrapper), (object)))
#define Wrapper_SetContext(wrapper, context) \
        (_wrapper_api->setcontext((wrapper), (context)))

#endif

#endif

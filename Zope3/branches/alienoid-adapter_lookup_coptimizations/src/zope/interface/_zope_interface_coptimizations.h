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

/*
  $Id$
*/
#ifndef Py_ZOPE_INTERFACE_COPTIMIZATIONS_H
#define Py_ZOPE_INTERFACE_COPTIMIZATIONS_H

#ifdef __cplusplus
extern "C" {
#endif

/* C API functions */
#define providedBy_NUM 0
#define providedBy_RETURN PyObject *
#define providedBy_PROTO (PyObject *ignored, PyObject *ob)

/* Total number of C API pointers */
#define Interface_API_pointers 1


#ifdef _ZOPE_INTERFACE_COPTIMIZATIONS
/* This section is used when compiling _zope_interface_coptimizations.c */

static providedBy_RETURN providedBy providedBy_PROTO;

#else
/* This section is used in modules that uses
   _zope_interface_coptimizations's API
*/

static void **Interface_API;

#define providedBy \
 (*(providedBy_RETURN (*)providedBy_PROTO) Interface_API[providedBy_NUM])

/* Return -1 and set exception on error, 0 on success. */
static int
import_zope_interface_coptimizations(void)
{
        PyObject *module;
        module = PyImport_ImportModule("_zope_interface_coptimizations");

        if (module != NULL) {
                PyObject *c_api_object = PyObject_GetAttrString(module,
                                                                "_C_API");
                if (c_api_object == NULL)
                        return -1;
                if (PyCObject_Check(c_api_object))
                        Interface_API = \
                                (void **)PyCObject_AsVoidPtr(c_api_object);
                Py_DECREF(c_api_object);
        }
        return 0;
}

#endif

#ifdef __cplusplus
}

#endif

#endif /* !defined(Py_ZOPE_INTERFACE_COPTIMIZATIONS_H) */

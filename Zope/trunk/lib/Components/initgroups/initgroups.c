/*****************************************************************************

  Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
  
  This software is subject to the provisions of the Zope Public License,
  Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
  WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
  WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
  FOR A PARTICULAR PURPOSE
  
 ****************************************************************************/

#include "Python.h"

#if defined(__unix__) || defined(unix)

#include <grp.h>
#include <sys/types.h>
#include <unistd.h>

static PyObject *
initgroups_initgroups(self, args)
PyObject *self;
PyObject *args;
{
	char *username;
	gid_t gid;

	if(!PyArg_ParseTuple(args, "sl", &username, &gid))
		return NULL;

	if(initgroups(username, gid) == -1)
		return PyErr_SetFromErrno(PyExc_OSError);

	Py_INCREF(Py_None);
	return Py_None;
}

static PyMethodDef InitgroupsMethods[] = {
	{"initgroups",	initgroups_initgroups,	METH_VARARGS},
	{NULL,		NULL}
};

#else

/* This module is empty on non-UNIX systems. */

static PyMethodDef InitgroupsMethods[] = {
	{NULL,		NULL}
};

#endif /* defined(__unix__) || defined(unix) */

void
initinitgroups()
{
	(void)Py_InitModule("initgroups", InitgroupsMethods);
}


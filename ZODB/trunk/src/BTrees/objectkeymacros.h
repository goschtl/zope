#define KEYMACROS_H "$Id: objectkeymacros.h,v 1.2 2001/03/20 13:52:00 jim Exp $\n"
#define KEY_TYPE PyObject *
#define TEST_KEY(KEY, TARGET) PyObject_Compare((KEY),(TARGET))
#define INCREF_KEY(k) Py_INCREF(k)
#define DECREF_KEY(KEY) Py_DECREF(KEY)
#define COPY_KEY(KEY, E) KEY=(E)
#define COPY_KEY_TO_OBJECT(O, K) O=(K); Py_INCREF(O)
#define COPY_KEY_FROM_ARG(TARGET, ARG, S) TARGET=(ARG)

##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Simple wrapper for ICU ucol API

$Id$
"""
import sys

cdef extern from  "unicode/utypes.h":

    ctypedef int UErrorCode
    ctypedef int int32_t
    ctypedef char uint8_t
    int U_FAILURE(UErrorCode status)
    UErrorCode U_ZERO_ERROR

cdef extern from  "unicode/utf.h":
    ctypedef int UChar
    ctypedef int UChar32

cdef extern from  "unicode/ustring.h":
    UChar *u_strFromUTF32(UChar *dest, int32_t destCapacity,
                          int32_t *pDestLength,
                          UChar32 *src, int32_t srcLength,
                          UErrorCode *status)

cdef extern from  "unicode/ucol.h":

    ctypedef struct UCollator:
        pass
    UCollator *ucol_open(char *locale, UErrorCode *status)
    void ucol_close(UCollator *collator)
    int32_t ucol_getSortKey(UCollator *coll,
                            UChar *source, int32_t sourceLength,
                            uint8_t *result,
                            int32_t resultLength
                            )

cdef extern from  "Python.h":

    cdef int PyUnicode_Check(ob)
    cdef int PyString_Check(ob)

    ctypedef int Py_UNICODE

    ctypedef class __builtin__.unicode [object PyUnicodeObject]:
        cdef int length
        cdef Py_UNICODE *str

    void *PyMem_Malloc(int)
    void PyMem_Free(void *p)
    object PyString_FromStringAndSize(char *v, int l)
    
cdef class UCharString:
    """Wrapper for ICU UChar arrays
    """

    cdef UChar *data
    cdef readonly int32_t length
    cdef readonly object base
    cdef readonly int need_to_free

    def __new__(self, unicode text):
        cdef int32_t buffsize
        cdef UErrorCode status

        if sizeof(Py_UNICODE) == 2:
            self.data = text.str
            self.length = text.length
            self.base = text
            self.need_to_free = 0
        else:
            buffsize = 2*text.length + 1
            self.data = <UChar*>PyMem_Malloc(buffsize*sizeof(UChar))
            status = 0
            u_strFromUTF32(self.data, buffsize, &(self.length),
                           <UChar32*>text.str, text.length, &status)
            self.need_to_free = 1
            if U_FAILURE(status):
                raise ValueError(
                    "Couldn't convert Python unicode data to ICU unicode data."
                    )

    def __dealloc__(self):
        if self.need_to_free and self.data != NULL:
            PyMem_Free(self.data)
            self.data = NULL


cdef class KeyFactory:
    """Compute a collation key for a unicode string.
    """

    cdef UCollator *collator

    def __new__(self, char *locale):
        cdef UCollator *collator
        cdef UErrorCode status
        status = U_ZERO_ERROR
        collator = ucol_open(locale, &status)
        if U_FAILURE(status):
            raise ValueError("Couldn't create a collator")
        self.collator = collator

    def __dealloc__(self):
        if self.collator != NULL:
            ucol_close(self.collator)

    def __call__(self, unicode text):
        """Compute a collation key for the given unicode text.

        Of course, the key is only valid for the given locale.
        """
        cdef char *buffer
        cdef int32_t bufsize
        cdef int32_t size

        icutext = UCharString(text)
        bufsize = (<UCharString>icutext).length*2
        buffer = <char*>PyMem_Malloc(bufsize)
        size = ucol_getSortKey(self.collator,
                               (<UCharString>icutext).data,
                               (<UCharString>icutext).length,
                               buffer, bufsize)
        if size > bufsize:
            bufsize = size
            PyMem_Free(buffer)
            buffer = <char*>PyMem_Malloc(bufsize)
            size = ucol_getSortKey(self.collator,
                                   (<UCharString>icutext).data,
                                   (<UCharString>icutext).length,
                                   buffer, bufsize)
            assert size == bufsize, ("size from ucol_getSortKey changed %d %d"
                                     % (size, bufsize))

        result = PyString_FromStringAndSize(buffer, size)
        PyMem_Free(buffer)
        return result

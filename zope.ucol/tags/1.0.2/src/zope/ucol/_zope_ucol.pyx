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

    cdef enum UErrorCode:
        U_USING_DEFAULT_WARNING = -127
        U_USING_FALLBACK_WARNING = -128
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
    int ucol_strcoll(UCollator *coll,
                     UChar *source, int32_t sourceLength,
                     UChar *target, int32_t targetLength)

cdef extern from  "Python.h":

    int PyUnicode_Check(ob)
    int PyString_Check(ob)

    ctypedef int Py_UNICODE
    Py_UNICODE *PyUnicode_AS_UNICODE(ob)
    int PyUnicode_GET_SIZE(ob)
    char *PyString_AS_STRING(ob)

    void *PyMem_Malloc(int size)
    void PyMem_Free(void *p)
    object PyString_FromStringAndSize(char *v, int l)
    
    
cdef class UCharString:
    """Wrapper for ICU UChar arrays
    """

    cdef UChar *data
    cdef readonly int32_t length
    cdef readonly object base
    cdef readonly int need_to_free

    def __new__(self, text):
        cdef int32_t buffsize
        cdef UErrorCode status
        cdef Py_UNICODE *str
        cdef int length

        if not PyUnicode_Check(text):
            if PyString_Check(text):
                text = unicode(text)
                assert PyUnicode_Check(text)
            else:
                raise TypeError("Expected unicode string")

        length = PyUnicode_GET_SIZE(text)
        str = PyUnicode_AS_UNICODE(text)
        

        if sizeof(Py_UNICODE) == 2:
            self.data = str
            self.length = length
            self.base = text
            self.need_to_free = 0
        else:
            buffsize = 2*length + 1
            self.data = <UChar*>PyMem_Malloc(buffsize*sizeof(UChar))
            if self.data == NULL:
                raise MemoryError
            status = 0
            u_strFromUTF32(self.data, buffsize, &(self.length),
                           <UChar32*>str, length, &status)
            assert self.length <= buffsize
            self.need_to_free = 1
            if U_FAILURE(status):
                raise ValueError(
                    "Couldn't convert Python unicode data to ICU unicode data."
                    )

    def __dealloc__(self):
        if self.need_to_free and self.data != NULL:
            PyMem_Free(self.data)
            self.data = NULL


cdef class Collator:
    """Compute a collation key for a unicode string.
    """

    cdef UCollator *collator
    cdef readonly object locale
    cdef readonly int used_default_information

    def __new__(self, locale):
        cdef UCollator *collator
        cdef UErrorCode status

        if not PyString_Check(locale):
            raise TypeError("String locale expected")
        
        status = U_ZERO_ERROR
        collator = ucol_open(PyString_AS_STRING(locale), &status)
        if U_FAILURE(status):
            raise ValueError("Couldn't create a collator")
        self.collator = collator
        self.locale = locale
        if (status == U_USING_DEFAULT_WARNING
            or
            status == U_USING_FALLBACK_WARNING):
            status = 1
        self.used_default_information = status

    def __dealloc__(self):
        if self.collator != NULL:
            ucol_close(self.collator)

    def key(self, text):
        """Compute a collation key for the given unicode text.

        Of course, the key is only valid for the given locale.
        """
        cdef char *buffer
        cdef int32_t bufsize
        cdef int32_t size

        icutext = UCharString(text)
        bufsize = (<UCharString>icutext).length*2+10

        # the +1 below is needed to avoid an apprent buffer overflow bug in ICU
        buffer = <char*>PyMem_Malloc(bufsize +1)
        if buffer == NULL:
            raise MemoryError
        size = ucol_getSortKey(self.collator,
                               (<UCharString>icutext).data,
                               (<UCharString>icutext).length,
                               <uint8_t*>buffer, bufsize)
        while size > bufsize:
            bufsize = size
            PyMem_Free(buffer)
            buffer = <char*>PyMem_Malloc(bufsize +1) # See above +1
            if buffer == NULL:
                raise MemoryError
            size = ucol_getSortKey(self.collator,
                                   (<UCharString>icutext).data,
                                   (<UCharString>icutext).length,
                                   <uint8_t*>buffer, bufsize)

        result = PyString_FromStringAndSize(buffer, size)
        PyMem_Free(buffer)
        return result

    def cmp(self, o1, o2):
        u1 = UCharString(o1)
        u2 = UCharString(o2)
        return ucol_strcoll(
            self.collator,
            (<UCharString>u1).data,
            (<UCharString>u1).length,
            (<UCharString>u2).data,
            (<UCharString>u2).length,
            )

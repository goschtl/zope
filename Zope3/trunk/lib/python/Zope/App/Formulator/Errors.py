##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
"""
Exception Classes for Formulator

$Id: Errors.py,v 1.2 2002/06/10 23:27:46 jim Exp $
"""

# These classes are placed here so that they can be imported into TTW Python
# scripts. To do so, add the following line to your Py script:
# from Products.Formulator.Errors import ValidationError, FormValidationError


class FormValidationError(Exception):

    def __init__(self, errors, result):
        Exception.__init__(self, "Form Validation Error")
        self.errors = errors
        self.result = result
        

class ValidationError(Exception):
    
    def __init__(self, errorKey, field):
        Exception.__init__(self, errorKey)
        self.errorKey = errorKey
        self.fieldId = field.id
        self.field = field
        self.errorText = field.getErrorMessage(errorKey)


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

$Id: Validator.py,v 1.2 2002/06/10 23:27:46 jim Exp $
"""

from Zope.App.Formulator.Errors import ValidationError
from IValidator import IValidator
from IInstanceFactory import IInstanceFactory

class Validator:
    """Validates input and possibly transforms it to output.
    """

    __implements__ = (
        IValidator,
        IInstanceFactory
        )
    
    propertyNames = ['externalValidator']
    externalValidator = None
    
    messageNames = ['externalValidatorFailed']
    externalValidatorFailed = "The input failed the external validator."


    def __init__(self, **kw):
        """Initialize the Validator."""
        for name in self.propertyNames:
            if name in kw.keys():
                setattr(self, name, kw[name])

                
    def getMessage(self, name):
        """ """
        if name in self.messageNames:
            return getattr(self, name)


    ############################################################
    # Implementation methods for interface
    # Zope.App.Formulator.IValidator.

    def raiseError(self, errorKey, field):
        '''See interface IValidator'''
        raise ValidationError(errorKey, field)


    def validate(self, field, value):
        '''See interface IValidator'''
        pass
    #
    ############################################################


    ############################################################
    # Implementation methods for interface
    # Zope.App.Formulator.IInstanceFactory.

    def __call__(self, context):
        '''See interface IInstanceFactory'''
        self.realize(context)
        return self

    def realize(self, context):
        '''See interface IInstanceFactory'''
        self.context = context
    #
    ############################################################

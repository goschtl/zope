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

$Id: Field.py,v 1.2 2002/06/10 23:27:46 jim Exp $
"""

from Persistence import Persistent
from IField import IField
from Zope.App.Formulator.Errors import ValidationError
from IInstanceFactory import IInstanceFactory


class Field(Persistent):
    """Base class of all fields.
    A field is an object consisting of a widget and a validator.
    """

    __implements__ = (
        IField,
        IInstanceFactory
        )

    propertyNames = ('id', 'validator', 'default', 'title', 'description',
                     'required')

    id = None
    validator = None
    default = None
    title = 'Field Title'
    description = 'Field Description'
    required = 0


    def __init__(self, context=None, **kw):
        self.realize(context)

        for name in self.propertyNames:
            if name in kw.keys():
                setattr(self, name, kw[name])


    def getErrorMessage(self, name):
        try:
            return self.validator.getMessage(name)
        except KeyError:
            if name in self.validator.messageNames:
                return getattr(self.validator, name)
            else:
                return "Unknown error: %s" % name


    ############################################################
    # Implementation methods for interface
    # Zope.App.Formulator.IField.

    def getValidator(self):
        '''See interface IField'''
        return self.validator


    def hasValue(self, id):
        '''See interface IField'''
        if id in self.propertyNames:
            return 1
        else:
            return 0


    def getValue(self, id, _default=None):
        '''See interface IField'''
        if id in self.propertyNames:
            return getattr(self, id)
        else:
            return _default


    def isRequired(self):
        '''See interface IField'''
        return hasattr(self, 'required') and getattr(self, 'required')


    def getErrorNames(self):
        '''See interface IField'''
        return self.validator.messageNames


    def getTales(self, id):
        '''See interface IField'''
        raise NotImplemented


    def isTALESAvailable(self):
        '''See interface IField'''
        raise NotImplemented


    def getOverride(self, id):
        '''See interface IField'''
        raise NotImplemented

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

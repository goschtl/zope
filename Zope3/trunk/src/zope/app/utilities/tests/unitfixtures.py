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
from zope.app.utilities.schema import SchemaUtility
from zope.interface.interface import Attribute
from zope.app.event.tests.placelesssetup import PlacelessSetup
# Setup EventPublication service.
PlacelessSetup().setUp()

Schema = SchemaUtility()
Schema.setName('Schema')

class mytest(Schema):
    pass

class C:
    def m1(self, a, b):
        "return 1"
        return 1

    def m2(self, a, b):
        "return 2"
        return 2

# testInstancesOfClassImplements




#  YAGNI IC=Interface.impliedInterface(C)
class IC(Schema):
    def m1(a, b):
        "return 1"

    def m2(a, b):
        "return 2"



C.__implements__=IC

class I1(Schema):
    def ma():
        "blah"

class I2(I1): pass

class I3(Schema): pass

class I4(Schema): pass

class A(I1.deferred()):
    __implements__=I1

class B:
    __implements__=I2, I3

class D(A, B): pass

class E(A, B):
    __implements__ = A.__implements__, C.__implements__


class FooInterface(Schema):
    """ This is an Abstract Base Class """

    def aMethod(foo, bar, bingo):
        """ This is aMethod """

    def anotherMethod(foo=6, bar="where you get sloshed", bingo=(1,3,)):
        """ This is anotherMethod """

    def wammy(zip, *argues):
        """ yadda yadda """

    def useless(**keywords):
        """ useless code is fun! """

FooInterface.addField('foobar', Attribute("fuzzed over beyond all recognition"))

class Foo:
    """ A concrete class """

    __implements__ = FooInterface,

    foobar = "yeah"

    def aMethod(self, foo, bar, bingo):
        """ This is aMethod """
        return "barf!"

    def anotherMethod(self, foo=6, bar="where you get sloshed", bingo=(1,3,)):
        """ This is anotherMethod """
        return "barf!"

    def wammy(self, zip, *argues):
        """ yadda yadda """
        return "barf!"

    def useless(self, **keywords):
        """ useless code is fun! """
        return "barf!"

foo_instance = Foo()

class Blah:
    pass

new = Schema.__class__
FunInterface = new('FunInterface')
BarInterface = new('BarInterface', [FunInterface])
BobInterface = new('BobInterface')
BazInterface = new('BazInterface', [BobInterface, BarInterface])

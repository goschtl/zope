# -*- coding: UTF-8 -*-
from zope.interface import implements
from zope.interface import Interface
import persistent

from ocql.testing.sample.interfaces import IStudent

class Student(persistent.Persistent):
    """A simple implementation of the gsoc student
    Make sure that the ‘‘Student‘‘ implements the ‘‘IStudent‘‘ interface:

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IStudent, Student)
    True

    Here is an example of changing the name of the student:
    >>> student = Student()
    >>> student.name
    u''

    >>> student.name = u'Student Name'
    >>> student.name
    u'Student Name'
    """

    implements(IStudent)

    name = u''

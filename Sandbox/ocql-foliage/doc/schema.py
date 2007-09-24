# -*- coding: UTF-8 -*-

from zope.interface import Interface
from zope.schema import TextLine, Int, Choice, Set, List

class IAddress(Interface):
    street = TextLine(
        title=u"Street address",
        required=True
        )

class IDepartment(Interface):
    address = Choice(
        title=u"Street address",
        vocabulary="vocab_of_IAddress",
        required=True
        )

class ICourse(Interface):
    code = TextLine(
        title=u"Course code",
        required=True
        )
    runBy = Set(
        title=u"Run by",
        value_type = Choice(
            title=u"Department",
            vocabulary="vocab_of_IDepartment",
            )
        )
    prerequisites = Set(
        title=u"Prerequisite courses",
        value_type = Choice(
            title=u"Course",
            vocabulary="vocab_of_ICourse",
            )
        )
    salary = Int(
        title=u"Credits",
        )
    assessment = List(
        title=u"Assessment",
        value_type = Int(
            title=u"Assessment",
            )
        )

class IPerson(Interface):
    name = TextLine(
        title=u"Name",
        required=True
        )

class IStaff(IPerson):
    department = Choice(
        title=u"Department",
        vocabulary="vocab_of_IDepartment",
        )
    teaches = Set(
        title=u"Teaches",
        value_type = Choice(
            title=u"Course",
            vocabulary="vocab_of_ICourse",
            )
        )
    salary = Int(
        title=u"Name",
        )

class IStudent(IPerson):
    major = Choice(
        title=u"Department",
        vocabulary="vocab_of_IDepartment",
        )
    supervisedBy = List(
        title=u"Supervised by",
        value_type = Choice(
            title=u"Member of staff",
            vocabulary="vocab_of_IStaff",
            )
        )
    takes = Set(
        title=u"Takes",
        value_type = Choice(
            title=u"Course",
            vocabulary="vocab_of_ICourse",
            )
        )

class ITutor(IStaff, IStudent):
    #salary = Int(
    #    title=u"Name",
    #    required=True
    #    )
    pass

class IVisitingStaff(IStaff):
    pass

catalog.addValueIndex(IDepartment['address'], multiple=False)
catalog.addValueIndex(ICourse['runBy'], multiple=True)
catalog.addValueIndex(ICourse['prerequisites'], multiple=True)
catalog.addValueIndex(IStudent['major'], multiple=False)
catalog.addValueIndex(IStudent['supervisedBy'], multiple=True)
catalog.addValueIndex(IStudent['takes'], multiple=True)
catalog.addValueIndex(IStaff['teaches'], multiple=True)
catalog.addValueIndex(IStaff['department'], multiple=False)
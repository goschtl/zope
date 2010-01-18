"""
This module tells megrok.traject how to map URLs to ORM-backed objects
and the non-persistent Departments object.
"""

import grok

from z3c.saconfig import Session
from sqlalchemy import and_
from megrok import traject

from trajectrdbexample.app import TrajectRDBExample, Departments
from trajectrdbexample import db

grok.context(TrajectRDBExample)

class FacultyTraject(traject.Traject):
    pattern = ':faculty_id:int'
    model = db.Faculty
    
    def factory(faculty_id):
        session = Session()
        return session.query(db.Faculty).filter(
            db.Faculty.id == faculty_id).first()

    def arguments(model):
        return {'faculty_id': model.id}

class DepartmentsTraject(traject.Traject):
    pattern = ':faculty_id:int/departments'
    model = Departments

    def factory(faculty_id):
        return Departments(faculty_id)

    def arguments(model):
        return {'faculty_id': model.faculty_id}

class DepartmentTraject(traject.Traject):
    # we browse to departments using the title attribute of
    # Department, which is assumed (or constrained) to be unique.
    pattern = ':faculty_id:int/departments/:department_title:str'
    model = db.Department

    def factory(faculty_id, department_title):
        session = Session()
        return session.query(db.Department).filter(
            and_(db.Department.faculty_id == faculty_id,
                 db.Department.title == department_title)).first()

    def arguments(model):
        return {'faculty_id': model.faculty.id,
                'department_title': model.title}

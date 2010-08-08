##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""

We create an app:

  >>> getRootFolder()["app"] = App()

We set up a test browser:

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
  >>> browser.handleErrors = False

We are going to look at the request.getURL() behavior of various
views. We need to get these right otherwise things break in a weird
way.

App::

  >>> browser.open("http://localhost/app")
  >>> print browser.contents
  http://localhost/app/@@index

App explicit index::

  >>> browser.open("http://localhost/app/@@index")
  >>> print browser.contents
  http://localhost/app/@@index

App explicit index without @@::

  >>> browser.open("http://localhost/app/index")
  >>> print browser.contents
  http://localhost/app/index

Departments::

  >>> browser.open("http://localhost/app/departments")
  >>> print browser.contents
  http://localhost/app/departments/@@index

Departments explicit index::

  >>> browser.open("http://localhost/app/departments/@@index")
  >>> print browser.contents
  http://localhost/app/departments/@@index

Departments explicit index without @@::

  >>> browser.open("http://localhost/app/departments/index")
  >>> print browser.contents
  http://localhost/app/departments/index

Department::

  >>> browser.open("http://localhost/app/departments/1")
  >>> print browser.contents
  http://localhost/app/departments/1/@@index

Department explicit index::

  >>> browser.open("http://localhost/app/departments/1/@@index")
  >>> print browser.contents
  http://localhost/app/departments/1/@@index

Department explicit index without @@::

  >>> browser.open("http://localhost/app/departments/1/index")
  >>> print browser.contents
  http://localhost/app/departments/1/index

Employees::

  >>> browser.open("http://localhost/app/departments/1/employees")
  >>> print browser.contents
  http://localhost/app/departments/1/employees/@@index

Employees explicit index::

  >>> browser.open("http://localhost/app/departments/1/employees/@@index")
  >>> print browser.contents
  http://localhost/app/departments/1/employees/@@index

Employees explicit index without @@::

  >>> browser.open("http://localhost/app/departments/1/employees/index")
  >>> print browser.contents
  http://localhost/app/departments/1/employees/index
  
Employee::

  >>> browser.open("http://localhost/app/departments/1/employees/2")
  >>> print browser.contents
  http://localhost/app/departments/1/employees/2/@@index

Employee explicit index::

  >>> browser.open("http://localhost/app/departments/1/employees/2/@@index")
  >>> print browser.contents
  http://localhost/app/departments/1/employees/2/@@index

Employee explicit index without @@::

  >>> browser.open("http://localhost/app/departments/1/employees/2/index")
  >>> print browser.contents
  http://localhost/app/departments/1/employees/2/index
  
"""

import grok

from megrok import traject

class Departments(grok.Model):
    pass

class Department(grok.Model):
    def __init__(self, department_id):
        self.department_id = department_id

class Employees(grok.Model):
    def __init__(self, department_id):
        self.department_id = department_id
    
class Employee(grok.Model):
    def __init__(self, department_id, employee_id):
        self.department_id = department_id
        self.employee_id = employee_id

class DepartmentsIndex(grok.View):
    grok.context(Departments)
    grok.name('index')
    def render(self):
        return self.request.getURL()

class DepartmentIndex(grok.View):
    grok.context(Department)
    grok.name('index')
    def render(self):
        return self.request.getURL()

class EmployeesIndex(grok.View):
    grok.context(Employees)
    grok.name('index')
    def render(self):
        return self.request.getURL()

class EmployeeIndex(grok.View):
    grok.context(Employee)
    grok.name('index')
    def render(self):
        return self.request.getURL()

class App(grok.Application, grok.Model):
    pass

class AppIndex(grok.View):
    grok.context(App)
    grok.name('index')
    def render(self):
        return self.request.getURL()
    
class DepartmentsTraject(traject.Traject):
    grok.context(App)

    pattern = 'departments'
    model = Departments

    def factory():
        return Departments()

    def arguments(department):
        return {}

class DepartmentTraject(traject.Traject):
    grok.context(App)

    pattern = 'departments/:department_id'
    model = Department

    def factory(department_id):
        try:
            department_id = int(department_id)
        except ValueError:
            return None
        return Department(department_id)

    def arguments(department):
        return dict(department_id=department.department_id)

class EmployeesTraject(traject.Traject):
    grok.context(App)

    pattern = 'departments/:department_id/employees'
    model = Employees

    def factory(department_id):
        try:
            department_id = int(department_id)
        except ValueError:
            return None
        return Employees(department_id)

    def arguments(employees):
        return dict(department_id=employees.department_id)

class EmployeeTraject(traject.Traject):
    grok.context(App)

    pattern = 'departments/:department_id/employees/:employee_id'
    model = Employee

    def factory(department_id, employee_id):
        try:
            department_id = int(department_id)
            employee_id = int(employee_id)
        except ValueError:
            return None
        return Employee(department_id, employee_id)

    def arguments(employee):
        return dict(
            department_id=employee.department_id,
            employee_id=employee.employee_id)

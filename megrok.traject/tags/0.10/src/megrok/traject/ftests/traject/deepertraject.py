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

Let's look at a department::

  >>> browser.open("http://localhost/app/departments/1")
  >>> print browser.contents
  Department: 1

We can also go to an employee::

  >>> browser.open("http://localhost/app/departments/1/employees/2")
  >>> print browser.contents
  Employee: 1 2

We cannot go to departments as there's no view for it::

  >>> browser.open("http://localhost/app/departments")
  Traceback (most recent call last):
    ...
  NotFound: Object: <megrok.traject.components.DefaultModel object at ...>,
  name: u'@@index'
    
Nor can we go to employees::

  >>> browser.open("http://localhost/app/departments/1/employees")
  Traceback (most recent call last):
    ...
  NotFound: Object: <megrok.traject.components.DefaultModel object at ...>,
  name: u'@@index'
"""

import grok

from megrok import traject

class Department(grok.Model):
    def __init__(self, department_id):
        self.department_id = department_id

class Employee(grok.Model):
    def __init__(self, department_id, employee_id):
        self.department_id = department_id
        self.employee_id = employee_id

class DepartmentIndex(grok.View):
    grok.context(Department)
    grok.name('index')
    def render(self):
        return 'Department: %s' % self.context.department_id

class EmployeeIndex(grok.View):
    grok.context(Employee)
    grok.name('index')
    def render(self):
        return 'Employee: %s %s' % (self.context.department_id,
                                    self.context.employee_id)

class App(grok.Application, grok.Model):
    pass

class DepartmentTraject(traject.Traject):
    grok.context(App)

    pattern = 'departments/:department_id'
    model = Department

    def factory(department_id):
        return Department(department_id)

    def arguments(department):
        return dict(department_id=department.department_id)

class EmployeeTraject(traject.Traject):
    grok.context(App)

    pattern = 'departments/:department_id/employees/:employee_id'
    model = Employee

    def factory(department_id, employee_id):
        return Employee(department_id, employee_id)

    def arguments(employee):
        return dict(
            department_id=employee.department_id,
            employee_id=employee.employee_id)

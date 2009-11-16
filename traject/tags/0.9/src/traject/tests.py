import unittest, doctest

from zope.interface import Interface, implements

import traject

class Default(object):
    def __init__(self, kw):
        self.kw = kw

def default(**kw):
    return Default(kw)

class Root(object):
    pass

class SubRoot(Root):
    pass

class Department(object):
    def __init__(self, department_id):
        self.department_id = department_id

class SubDepartment(Department):
    pass

class Employee(object):
    def __init__(self, department_id, employee_id):
        self.department_id = department_id
        self.employee_id = employee_id

class SubEmployee(Employee):
    pass

class EmployeeData(object):
    def __init__(self, department_id, employee_id):
        self.department_id = department_id
        self.employee_id = employee_id

class SpecialDepartment(object):
    def __init__(self):
        pass

class SpecialEmployee(object):
    def __init__(self, employee_id):
        self.employee_id = employee_id
        
class PatternsTestCase(unittest.TestCase):

    def test_simple_steps(self):
        self.assertEquals(
            ('a', 'b', 'c'),
            traject.parse('a/b/c'))
    
    def test_simple_steps_starting_slash(self):
        self.assertEquals(
            ('a', 'b', 'c'),
            traject.parse('/a/b/c'))

    def test_steps_with_variable(self):
        self.assertEquals(
            ('a', ':B', 'c'),
            traject.parse('a/:B/c'))

    def test_steps_with_double_variable_name(self):
        self.assertRaises(
            traject.ParseError,
            traject.parse, 'a/:B/c/:B')

    def test_subpatterns(self):
        self.assertEquals(
            [('a',),
             ('a', ':B'),
             ('a', ':B', 'c'),
             ],
            traject.subpatterns(
                ('a', ':B', 'c')
                ))

    def get_patterns(self):
        patterns = traject.Patterns()
        class Obj(object):
            def __init__(self, b, d):
                self.b = b
                self.d = d
        def f(b, d):
            return Obj(b, d)
        patterns.register(Root, 'a/:b/c/:d', f)
        return patterns, Obj
    
    def test_patterns_resolve_full_path(self):
        patterns, Obj = self.get_patterns()
        root = Root()
        
        # now that we have a pattern registered, we can try it
        obj = patterns.resolve(root, 'a/B/c/D', default)

        # we see that the parents and names are correct
        self.assertEquals('D', obj.__name__)
        self.assert_(isinstance(obj, Obj))
        obj = obj.__parent__
        self.assertEquals('c', obj.__name__)
        self.assert_(isinstance(obj, Default))
        obj = obj.__parent__
        self.assertEquals('B', obj.__name__)
        self.assert_(isinstance(obj, Default))
        obj = obj.__parent__
        self.assertEquals('a', obj.__name__)
        self.assert_(isinstance(obj, Default))
        obj = obj.__parent__
        self.assert_(isinstance(obj, Root))

    def test_patterns_resolve_stack_full_path(self):
        patterns, Obj = self.get_patterns()
        root = Root()

        l = ['a', 'B', 'c', 'D']
        l.reverse()

        obj = patterns.resolve_stack(root, l, default)

        # we see that the parents and names are correct
        self.assertEquals('D', obj.__name__)
        self.assert_(isinstance(obj, Obj))
        obj = obj.__parent__
        self.assertEquals('c', obj.__name__)
        self.assert_(isinstance(obj, Default))
        obj = obj.__parent__
        self.assertEquals('B', obj.__name__)
        self.assert_(isinstance(obj, Default))
        obj = obj.__parent__
        self.assertEquals('a', obj.__name__)
        self.assert_(isinstance(obj, Default))
        obj = obj.__parent__
        self.assert_(isinstance(obj, Root))

    def test_patterns_consume_stack_full_path(self):
        patterns, Obj = self.get_patterns()
        root = Root()

        l = ['a', 'B', 'c', 'D']
        l.reverse()

        unconsumed, consumed, obj = patterns.consume_stack(root, l, default)

        # have nothing left unconsumed
        self.assertEquals([], unconsumed)
        # everything was consumed
        self.assertEquals(['a', 'B', 'c', 'D'], consumed)
        
        # we see that the parents and names are correct
        self.assertEquals('D', obj.__name__)
        self.assert_(isinstance(obj, Obj))
        obj = obj.__parent__
        self.assertEquals('c', obj.__name__)
        self.assert_(isinstance(obj, Default))
        obj = obj.__parent__
        self.assertEquals('B', obj.__name__)
        self.assert_(isinstance(obj, Default))
        obj = obj.__parent__
        self.assertEquals('a', obj.__name__)
        self.assert_(isinstance(obj, Default))
        obj = obj.__parent__
        self.assert_(isinstance(obj, Root))

    def test_patterns_resolve_partial_path(self):
        patterns, Obj = self.get_patterns()
        root = Root()
        
        # let's try resolving a partial path
        obj = patterns.resolve(root, 'a/B/c', default)

        # we get a bunch of default objects
        self.assertEquals('c', obj.__name__)
        self.assert_(isinstance(obj, Default))
        obj = obj.__parent__
        self.assertEquals('B', obj.__name__)
        self.assert_(isinstance(obj, Default))
        obj = obj.__parent__
        self.assertEquals('a', obj.__name__)
        self.assert_(isinstance(obj, Default))
        obj = obj.__parent__
        self.assert_(isinstance(obj, Root))

    def test_patterns_consume_tack_partial_path(self):
        patterns, Obj = self.get_patterns()
        root = Root()
        
        # let's try resolving a partial path
        l = ['a', 'B', 'c']
        l.reverse()
        
        unconsumed, consumed, obj = patterns.consume_stack(root, l, default)

        self.assertEquals([], unconsumed)
        self.assertEquals(['a', 'B', 'c'], consumed)
        
        # we get a bunch of default objects
        self.assertEquals('c', obj.__name__)
        self.assert_(isinstance(obj, Default))
        obj = obj.__parent__
        self.assertEquals('B', obj.__name__)
        self.assert_(isinstance(obj, Default))
        obj = obj.__parent__
        self.assertEquals('a', obj.__name__)
        self.assert_(isinstance(obj, Default))
        obj = obj.__parent__
        self.assert_(isinstance(obj, Root))

    def test_patterns_resolve_impossible_path(self):
        patterns, Obj = self.get_patterns()
        root = Root()
        
        # let's try resolving something that doesn't go anywhere
        self.assertRaises(traject.ResolutionError,
                          patterns.resolve, root, 'b/c/d', default)

    def test_patterns_resolve_stack_impossible_path(self):
        patterns, Obj = self.get_patterns()
        root = Root()
        
        # let's try resolving something that doesn't go anywhere
        l = ['b', 'c', 'd']
        l.reverse()
        self.assertRaises(traject.ResolutionError,
                          patterns.resolve_stack, root, l, default)

    def test_patterns_consume_stack_impossible_path(self):
        patterns, Obj = self.get_patterns()
        root = Root()

        l = ['b', 'c', 'd']
        l.reverse()
        
        unconsumed, consumed, obj = patterns.consume_stack(root, l, default)

        self.assert_(obj is root)
        self.assertEquals(['d', 'c', 'b'], unconsumed)
        self.assertEquals([], consumed)
        
    def test_wrong_arguments(self):
        patterns = traject.Patterns()
        class Obj(object):
            def __init__(self, b, d):
                self.b = b
                self.d = d
        # different arguments than expected from path
        def f(a, c):
            return Obj(a, c)
        patterns.register(Root, 'a/:b/c/:d', f)

        root = Root()
    
        # let's try resolving it
        self.assertRaises(TypeError, patterns.resolve, root, 'a/B/c/D', default)

    def test_resolve_to_factory_that_returns_none(self):
        patterns = traject.Patterns()
        class Model(object):
            def __init__(self, id):
                self.id = id
        def factory(id):
            # only return a model if the id is an int
            try:
                id = int(id)
            except ValueError:
                return None
            return Model(id)
        patterns.register(Root, 'models/:id', factory)
        root = Root()

        self.assertRaises(traject.ResolutionError, patterns.resolve,
                          root, 'models/not_an_int', default)
        
    def test_consume_to_factory_that_returns_none(self):
        patterns = traject.Patterns()
        class Model(object):
            def __init__(self, id):
                self.id = id
        def factory(id):
            # only return a model if the id is an int
            try:
                id = int(id)
            except ValueError:
                return None
            return Model(id)
        patterns.register(Root, 'models/:id', factory)
        root = Root()

        unconsumed, consumed, obj = patterns.consume(root,
                                                     'models/not_an_int',
                                                     default)
        self.assertEquals(['not_an_int'], unconsumed)
        self.assertEquals(['models'], consumed)
        self.assertEquals('models', obj.__name__)
        self.assert_(obj.__parent__ is root)
        
    def get_multi_patterns(self):
        patterns = traject.Patterns()
        patterns.register(Root, 'departments/:department_id',
                          Department)
        patterns.register(Root,
                          'departments/:department_id/employees/:employee_id',
                          Employee)
        return patterns
    
    def test_multiple_registrations_resolve_to_child(self):
        patterns = self.get_multi_patterns()
        root = Root()

        obj = patterns.resolve(root, u'departments/1/employees/10', default)

        self.assert_(isinstance(obj, Employee))
        self.assertEquals(u'1', obj.department_id)
        self.assertEquals(u'10', obj.employee_id)

    def test_multiple_registrations_consume_to_child_and_view(self):
        patterns = self.get_multi_patterns()
        root = Root()

        unconsumed, consumed, obj = patterns.consume(
            root, u'departments/1/employees/10/index',
            default)

        self.assertEquals(['index'], unconsumed)
        self.assertEquals(['departments', '1', 'employees', '10'],
                          consumed)
        self.assert_(isinstance(obj, Employee))
        self.assertEquals(u'1', obj.department_id)
        self.assertEquals(u'10', obj.employee_id)

    def test_multiple_registrations_resolve_to_parent(self):
        patterns = self.get_multi_patterns()
        root = Root()
    
        obj = patterns.resolve(root, u'departments/1', default)

        self.assert_(isinstance(obj, Department))
        self.assertEquals(u'1', obj.department_id)

    def test_multiple_registrations_consume_to_parent_and_view(self):
        patterns = self.get_multi_patterns()
        root = Root()
    
        unconsumed, consumed, obj = patterns.consume(
            root, u'departments/1/index', default)

        self.assertEquals(['index'], unconsumed)
        self.assertEquals(['departments', '1'], consumed)
        
        self.assert_(isinstance(obj, Department))
        self.assertEquals(u'1', obj.department_id)

    def test_multiple_registrations_resolve_to_nonexistent(self):
        patterns = self.get_multi_patterns()
        root = Root()

        # we will also test resolving a URL that doesn't work at all
        self.assertRaises(traject.ResolutionError,
                          patterns.resolve, root, u'foo/1/bar', default)

    def get_overlapping_patterns(self):
        patterns = self.get_multi_patterns()
        # we register two things for the same path, a variable and a step
        patterns.register(Root,
                          'departments/special',
                          SpecialDepartment)
        return patterns
    
    def test_overlapping_variable_and_step_resolve_to_child(self):
        patterns = self.get_overlapping_patterns()
        root = Root()
        
        obj = patterns.resolve(root, u'departments/1/employees/10', default)

        self.assert_(isinstance(obj, Employee))
        self.assertEquals(u'1', obj.department_id)
        self.assertEquals(u'10', obj.employee_id)

    def test_overlapping_variable_and_step_resolve_to_parent(self):
        patterns = self.get_overlapping_patterns()
        root = Root()
                
        obj = patterns.resolve(root, u'departments/1', default)

        self.assert_(isinstance(obj, Department))
        self.assertEquals(u'1', obj.department_id)

    def test_overlapping_variable_and_step_resolve_to_step(self):
        patterns = self.get_overlapping_patterns()
        root = Root()
       
        # we can also get to the special department. the step will have
        # priority over the variable
        obj = patterns.resolve(root, u'departments/special', default)
        self.assert_(isinstance(obj, SpecialDepartment))

    def test_overlapping_variable_and_step_resolve_to_step_nonexistent(self):
        patterns = self.get_overlapping_patterns()
        root = Root()
 
        # sub-paths from special haven't been registered, so don't exist
        self.assertRaises(
            traject.ResolutionError,
            patterns.resolve, root, u'/departments/special/employees/10',
            default)

    def test_overlapping_variable_and_step_resolve_to_step_subpath(self):
        patterns = self.get_overlapping_patterns()
        root = Root()
       
        patterns.register(Root,
                          'departments/special/employees/:employee_id',
                          SpecialEmployee)
        obj = patterns.resolve(root, u'/departments/special/employees/10',
                               default)
        self.assert_(isinstance(obj, SpecialEmployee))


    def test_factory_override(self):
        patterns = self.get_multi_patterns()
        # for SubRoot we use a different factory
        patterns.register(SubRoot,
                          'departments/:department_id/employees/:employee_id',
                         SubEmployee)
       
        subroot = SubRoot()
        
        obj = patterns.resolve(subroot,
                               u'departments/1/employees/10', default)

        self.assert_(obj.__class__ is SubEmployee)
        self.assertEquals(u'1', obj.department_id)
        self.assertEquals(u'10', obj.employee_id)

    def test_factory_override_root_stays_the_same(self):
        patterns = self.get_multi_patterns()
        # for SubRoot we use a different factory
        patterns.register(SubRoot,
                          'departments/:department_id/employees/:employee_id',
                          SubEmployee)
       
        root = Root()

        # we don't resolve for subroot but for root
        obj = patterns.resolve(root,
                               u'departments/1/employees/10', default)
        
        self.assert_(obj.__class__ is Employee)
        self.assertEquals(u'1', obj.department_id)
        self.assertEquals(u'10', obj.employee_id)

    def test_factory_extra_path(self):
        patterns = self.get_multi_patterns()
        # for SubRoot we add a path
        patterns.register(
            SubRoot,
            'departments/:department_id/employees/:employee_id/data',
            EmployeeData)

        subroot = SubRoot()
        
        obj = patterns.resolve(subroot,
                               u'departments/1/employees/10/data', default)

        self.assert_(obj.__class__ is EmployeeData)
        self.assertEquals(u'1', obj.department_id)
        self.assertEquals(u'10', obj.employee_id)

    def test_factory_extra_path_absent_with_root(self):
        patterns = self.get_multi_patterns()
        # for SubRoot we add a path
        patterns.register(
            SubRoot,
            'departments/:department_id/employees/:employee_id/data',
            EmployeeData)

        root = Root()
        
        self.assertRaises(traject.ResolutionError,
                          patterns.resolve, root,
                          u'departments/1/employees/10/data', default)

    def test_factory_override_in_mid_path(self):
        patterns = self.get_multi_patterns()
        patterns.register(
            SubRoot,
            'departments/:department_id',
            SubDepartment)

        subroot = SubRoot()
        
        obj = patterns.resolve(subroot,
                               u'departments/1/employees/10', default)

        employees = obj.__parent__
        department = employees.__parent__
        self.assert_(department.__class__ is
                     SubDepartment)

    def test_factory_original_in_mid_path(self):
        patterns = self.get_multi_patterns()
        patterns.register(
            SubRoot,
            'departments/:department_id',
            SubDepartment)

        root = Root()
        
        obj = patterns.resolve(root,
                               u'departments/1/employees/10', default)

        employees = obj.__parent__
        department = employees.__parent__
        self.assert_(department.__class__ is
                     Department)

    def test_conflicting_variable_names(self):
        patterns = traject.Patterns()
        patterns.register(
            Root, 'departments/:department_id',
            Department)
        self.assertRaises(
            traject.RegistrationError,
            patterns.register,
            Root, 'departments/:other_id', Department)
        self.assertRaises(
            traject.RegistrationError,
            patterns.register,
            Root, 'departments/:other_id/employees/:employee_id', Employee)

    def test_override_variable_names(self):
        patterns = traject.Patterns()
        patterns.register(
            Root, 'departments/:department_id',
            Department)
        class OtherDepartment(object):
            def __init__(self, other_id):
                self.other_id = other_id
        patterns.register(
            SubRoot, 'departments/:other_id',
            OtherDepartment)
        root = Root()
        subroot = SubRoot()
        department = patterns.resolve(
            root,
            u'departments/1', default)
        other_department = patterns.resolve(
            subroot,
            u'departments/1', default)
        
        self.assert_(Department == department.__class__)
        self.assert_(OtherDepartment == other_department.__class__)
        self.assertEquals(u'1', other_department.other_id)

    def test_conflict_in_override_variable_names(self):
        patterns = traject.Patterns()
        patterns.register(
            Root, 'departments/:department_id',
            Department)
        class OtherDepartment(object):
            def __init__(self, other_id):
                self.other_id = other_id
        patterns.register(
            SubRoot, 'departments/:other_id',
            OtherDepartment)
        patterns.register(
            Root, 'departments/:department_id/employees/:employee_id',
            Employee)
        subroot = SubRoot()
        # we cannot create Department because we got an other_id..
        self.assertRaises(TypeError,
                          patterns.resolve,
                          subroot, 'departments/1/employees/2', default)
        
    def test_resolved_conflict_in_override_variable_names(self):
        patterns = traject.Patterns()
        patterns.register(
            Root, 'departments/:department_id',
            Department)
        class OtherDepartment(object):
            def __init__(self, other_id):
                self.other_id = other_id
        patterns.register(
            SubRoot, 'departments/:other_id',
            OtherDepartment)
        patterns.register(
            Root, 'departments/:department_id/employees/:employee_id',
            Employee)

        # this sets up a conflicting situation when patterns are
        # resolved from subroot. We can resolve it by another registration
        class OtherEmployee(object):
            def __init__(self, other_id, employee_id):
                self.other_id = other_id
                self.employee_id = employee_id
        patterns.register(
            SubRoot, 'departments/:other_id/employees/:employee_id',
            OtherEmployee)
        
        subroot = SubRoot()
        obj = patterns.resolve(
            subroot, 'departments/1/employees/2', default)
        self.assert_(OtherEmployee is obj.__class__)
        self.assert_(OtherDepartment is obj.__parent__.__parent__.__class__)

    def test_register_pattern_on_interface(self):
        patterns = traject.Patterns()
        class ISpecialRoot(Interface):
            pass
        class SpecialRoot(object):
            implements(ISpecialRoot)
        class Obj(object):
            def __init__(self, b, d):
                self.b = b
                self.d = d
        patterns.register(ISpecialRoot, 'a/:b/c/:d', Obj)

        special_root = SpecialRoot()
        obj = patterns.resolve(
            special_root, 'a/B/c/D', default)
        self.assert_(isinstance(obj, Obj))
        self.assertEquals('B', obj.b)
        self.assertEquals('D', obj.d)
    

    # XXX need a test for trailing slash?

    # XXX could already introspect function to see whether we can properly
    # register it?

# factories that can retain previously created employees and departments
_department = {}
_employee = {}
_departments = None
_employees = None
# we can keep a record of how many times things were called
_calls = []

class Departments(object):
    pass

def identityDepartments():
    _calls.append("departments")
    global _departments
    if _departments is not None:
        return _departments
    _departments = Departments()
    return _departments

def identityDepartment(department_id):
    _calls.append("department %s" % department_id)
    department = _department.get(department_id)
    if department is None:
        _department[department_id] = department = Department(department_id)
    return department

class Employees(object):
    def __init__(self, department_id):
        self.department_id = department_id

def identityEmployees(department_id):
    _calls.append("employees %s" % department_id)
    global _employees
    if _employees is not None:
        return _employees
    _employees = Employees(department_id)
    return _employees

def identityEmployee(department_id, employee_id):
    _calls.append("employee %s %s" % (department_id, employee_id))
    employee = _employee.get((department_id, employee_id))
    if employee is None:
        _employee[(department_id, employee_id)] = employee = Employee(
            department_id, employee_id)
    return employee

class InverseTestCase(unittest.TestCase):
    def setUp(self):
        global _departments
        _departments = None
        global department
        _department.clear()
        global _employees
        _employees = None
        global employee
        _employee.clear()
        global _calls
        _calls = []
  
    def get_identity_patterns(self):
        patterns = traject.Patterns()
        patterns.register(Root, 'departments/:department_id',
                          identityDepartment)
        patterns.register(Root,
                          'departments/:department_id/employees/:employee_id',
                          identityEmployee)
        patterns.register(Root, 'departments',
                          identityDepartments)
        patterns.register(Root,
                          'departments/:department_id/employees',
                          identityEmployees)
    
        def employee_arguments(employee):
            return dict(employee_id=employee.employee_id,
                        department_id=employee.department_id)
    
        patterns.register_inverse(
            Root,
            Employee,
            u'departments/:department_id/employees/:employee_id',
            employee_arguments)

        return patterns

    def get_identity_patterns_complete(self):
        patterns = traject.Patterns()
        patterns.register(Root, 'departments/:department_id',
                          identityDepartment)
        patterns.register(Root,
                          'departments/:department_id/employees/:employee_id',
                          identityEmployee)
        patterns.register(Root, 'departments',
                          identityDepartments)
        patterns.register(Root,
                          'departments/:department_id/employees',
                          identityEmployees)
    
        def employee_arguments(employee):
            return dict(employee_id=employee.employee_id,
                        department_id=employee.department_id)
        def employees_arguments(employees):
            return dict(department_id=employees.department_id)
        def department_arguments(department):
            return dict(department_id=department.department_id)
        def departments_arguments(departments):
            return {}

        patterns.register_inverse(
            Root,
            Employee,
            u'departments/:department_id/employees/:employee_id',
            employee_arguments)
        patterns.register_inverse(
            Root,
            Employees,
            u'departments/:department_id/employees',
            employees_arguments)
        patterns.register_inverse(
            Root,
            Department,
            u'departments/:department_id',
            department_arguments)
        patterns.register_inverse(
            Root,
            Departments,
            u'departments',
            departments_arguments)
        return patterns
        
    def test_inverse(self):
        patterns = self.get_identity_patterns()
        root = Root()

        employee = Employee(u'1', u'2')
        patterns.locate(root, employee, default)

        self.assertEquals(u'2', employee.__name__)
        employees = employee.__parent__
        self.assertEquals(u'employees', employees.__name__)
        department = employees.__parent__
        self.assertEquals(u'1', department.__name__)
        self.assert_(isinstance(department, Department))
        departments = department.__parent__
        self.assertEquals(u'departments', departments.__name__)
        self.assert_(root is departments.__parent__)

    def test_identity(self):
        patterns = self.get_identity_patterns()
        root = Root()

        employee1 = patterns.resolve(
            root, u'departments/1/employees/2', default)
        employee2 = patterns.resolve(
            root, u'departments/1/employees/2', default)
        self.assert_(employee1 is employee2)
        employee3 = patterns.resolve(
            root, u'departments/1/employees/3', default)
        self.assert_(employee1 is not employee3)

    def test_no_recreation(self):
        patterns = self.get_identity_patterns()
        root = Root()

        # the first time we do an inverse lookup, it will recreate
        # department
        employee = identityEmployee(u'1', u'2')
        patterns.locate(root, employee, default)
        global _calls
        _calls = []
        # if won't create anything the second time
        patterns.locate(root, employee, default)
        self.assertEquals([], _calls)

    def test_cannot_locate(self):
        patterns = self.get_identity_patterns()
        root = Root()

        department = identityDepartment(u'1')
        self.assertRaises(traject.LocationError,
                          patterns.locate, root, department, default)

    def test_no_recreation_of_departments(self):
        patterns = self.get_identity_patterns_complete()
        root = Root()

        department = identityDepartment(u'1')
        patterns.locate(root, department, default)

        global _calls
        _calls = []
        # if won't recreate departments the second time
        # as it will find a Department object with a parent
        employee = identityEmployee(u'1', u'2')
        patterns.locate(root, employee, default)
        self.assertEquals([u'employee 1 2', u'employees 1', u'department 1'],
                          _calls)

    def test_no_recreation_of_department(self):
        patterns = self.get_identity_patterns_complete()
        root = Root()

        employees = identityEmployees(u'1')
        patterns.locate(root, employees, default)

        global _calls
        _calls = []
        # if won't recreate department the second time
        # as it will find a employees object with a parent
        employee = identityEmployee(u'1', u'2')
        patterns.locate(root, employee, default)
        self.assertEquals([u'employee 1 2', u'employees 1'],
                          _calls)

    def test_no_recreation_of_department_after_resolve(self):
        patterns = self.get_identity_patterns_complete()
        root = Root()

        # usually location is done after resolution, causing one lookup
        # of a parent for each object to be located below
        patterns.resolve(root, u'departments/1/employees', default)
        
        global _calls
        _calls = []
        # if won't recreate department the second time
        # as it will find a employees object with a parent
        employee = identityEmployee(u'1', u'2')
        patterns.locate(root, employee, default)
        self.assertEquals([u'employee 1 2', u'employees 1'],
                          _calls)
    def test_inverse_non_unicode_name(self):
        patterns = self.get_identity_patterns()

        root = Root()
        employee = identityEmployee(1, 2)
        patterns.locate(root, employee, default)

        self.assertEquals(u'2', employee.__name__)
        
    # test behavior of interfaces and overrides with inverse


def test_suite():
    optionflags=(doctest.ELLIPSIS+
                 doctest.NORMALIZE_WHITESPACE+
                 doctest.REPORT_NDIFF)
    
    suite = unittest.TestSuite()
    suite.addTests([
            unittest.makeSuite(PatternsTestCase),
            unittest.makeSuite(InverseTestCase),
            doctest.DocFileSuite('traject.txt',
                                 optionflags=optionflags)
            ])
    return suite

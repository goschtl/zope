import time
import traject

class Root(object):
    pass

class Department(object):
    def __init__(self, department_id):
        self.department_id = department_id

class Employee(object):
    def __init__(self, department_id, employee_id):
        self.department_id = department_id
        self.employee_id = employee_id

class Default(object):
    def __init__(self, **kw):
        self.kw = kw

def main():    
    patterns = traject.Patterns()
    patterns.register(Root,
                      'departments/:department_id/employees/:employee_id',
                      Employee)
    patterns.register(Root,
                      'departments/:department_id',
                      Department)
    amount = 1000
    root = Root()
    s = time.time()

    for i in range(amount):
        obj = patterns.resolve(root, 'departments/1/employees/2', Default)
    
    e = time.time()

    elapsed = e - s
    print "elapsed:", elapsed
    print "resolutions per second:", amount / elapsed
    print "time per resolution:", elapsed / amount
    
if __name__ == '__main__':
    main()

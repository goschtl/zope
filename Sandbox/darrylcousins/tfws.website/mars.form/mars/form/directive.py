from martian.directive import (InterfaceOrClassDirective,
                               ClassDirectiveContext)

view = InterfaceOrClassDirective('mars.form.view',
                           ClassDirectiveContext())
field = InterfaceOrClassDirective('mars.form.field',
                           ClassDirectiveContext())
widget = InterfaceOrClassDirective('mars.form.widget',
                           ClassDirectiveContext())


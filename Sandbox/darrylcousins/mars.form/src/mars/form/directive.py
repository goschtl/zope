from martian.directive import (InterfaceOrClassDirective,
                               SingleTextDirective,
                               ClassDirectiveContext)

mode = SingleTextDirective('mars.form.mode',
                           ClassDirectiveContext())
view = InterfaceOrClassDirective('mars.form.view',
                           ClassDirectiveContext())
field = InterfaceOrClassDirective('mars.form.field',
                           ClassDirectiveContext())
widget = InterfaceOrClassDirective('mars.form.widget',
                           ClassDirectiveContext())


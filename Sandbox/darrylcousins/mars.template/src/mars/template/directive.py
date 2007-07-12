from martian.directive import (InterfaceOrClassDirective,
                               SingleTextDirective,
                               ClassDirectiveContext)

macro = SingleTextDirective('mars.template.macro',
                           ClassDirectiveContext())
content_type = SingleTextDirective('mars.template.content_type',
                           ClassDirectiveContext())
mode = SingleTextDirective('mars.template.mode',
                           ClassDirectiveContext())
view = InterfaceOrClassDirective('mars.template.view',
                           ClassDirectiveContext())
field = InterfaceOrClassDirective('mars.template.field',
                           ClassDirectiveContext())
widget = InterfaceOrClassDirective('mars.template.widget',
                           ClassDirectiveContext())


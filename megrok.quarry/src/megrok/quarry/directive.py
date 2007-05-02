from grok.directive import InterfaceOrClassDirective, ClassOrModuleDirectiveContext
from grok.directive import SingleTextDirective, ClassDirectiveContext

layer = InterfaceOrClassDirective('quarry.layer',
                           ClassOrModuleDirectiveContext())

template = SingleTextDirective('quarry.template', ClassDirectiveContext())

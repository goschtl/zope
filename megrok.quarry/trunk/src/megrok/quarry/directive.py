from grok.directive import InterfaceOrClassDirective, ClassOrModuleDirectiveContext, InterfaceDirective
from grok.directive import SingleTextDirective, ClassDirectiveContext

layer = InterfaceOrClassDirective('quarry.layer',
                           ClassOrModuleDirectiveContext())

template = SingleTextDirective('quarry.template', ClassDirectiveContext())


viewletmanager = InterfaceOrClassDirective('quarry.viewletmanager',
                                           ClassDirectiveContext())
talnamespace = InterfaceDirective('quarry.talnamespace',
                               ClassDirectiveContext())

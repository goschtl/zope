import martian
import grokcore.component

from megrok.z3cform.wizard import components
from z3c.wizard.zcml import wizardStepDirective
from grokcore.view.meta.views import default_view_name


class WizardStepGrokker(martian.ClassGrokker):
    martian.component(components.BaseStep)
    martian.directive(grokcore.component.context)
    martian.directive(grokcore.component.name, get_default=default_view_name)

    def execute(self, factory, config, context, name, **kw):

        wizardStepDirective(config, factory, name,
                            'zope.Public', wizard=context)
        return True


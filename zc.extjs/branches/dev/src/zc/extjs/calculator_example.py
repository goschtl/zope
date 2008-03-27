import zc.extjs.application
import zope.exceptions

class Calculator(zc.extjs.application.Trusted,
                 zc.extjs.application.Application):

    resource_library_name = 'zc.extjs.calculator_example'

    @zc.extjs.application.jsonpage
    def about(self):
        return 'Calculator 1.0'

    @zc.extjs.application.jsonpage
    def operations(self):
        return ['add', "subtract"]

    @zc.extjs.application.jsonpage
    def value(self):
        return dict(value=getattr(self.context, 'calculator_value', 0))

    def do_add(self, value):
        value += getattr(self.context, 'calculator_value', 0)
        self.context.calculator_value = value
        return dict(value=value)
    
    @zc.extjs.application.jsonpage
    def add(self, value):
        if not isinstance(value, int):
            return dict(error="The value must be an integer!")
        return self.do_add(value)
    
    @zc.extjs.application.jsonpage
    def subtract(self, value):
        if not isinstance(value, int):
            raise zope.exceptions.UserError(
                "The value must be an integer!")
        return self.do_add(-value)

    @zc.extjs.application.jsonpage
    def noop(self):
        pass

    @zc.extjs.application.page
    def none(self):
        return "null"

    @zc.extjs.application.jsonpage
    def echo_form(self):
        return dict(self.request.form)


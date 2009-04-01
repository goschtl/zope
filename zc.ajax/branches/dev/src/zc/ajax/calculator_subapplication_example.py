import zc.ajax.application
import zope.exceptions

class Container(zc.ajax.application.Application):

    resource_library_name = 'zc.ajax'

    @property
    def calc(self):
        return Calculator(self.context, self.request, base_href='calc')


class Calculator(zc.ajax.application.Trusted,
                 zc.ajax.application.SubApplication,
                 zc.ajax.application.PublicTraversable,
                 ):

    @zc.ajax.application.jsonpage
    def operations(self):
        return [['add', self.base_href+'/add'],
                ['add', self.base_href+'/subtract'],
                ]
                
    @zc.ajax.application.jsonpage
    def value(self):
        return dict(value=getattr(self.context, 'calculator_value', 0))

    def do_add(self, value):
        value += getattr(self.context, 'calculator_value', 0)
        self.context.calculator_value = value
        return dict(value=value)
    
    @zc.ajax.application.jsonpage
    def add(self, value):
        if not isinstance(value, int):
            return dict(error="The value must be an integer!")
        return self.do_add(value)
    
    @zc.ajax.application.jsonpage
    def subtract(self, value):
        if not isinstance(value, int):
            raise zope.exceptions.UserError(
                "The value must be an integer!")
        return self.do_add(-value)


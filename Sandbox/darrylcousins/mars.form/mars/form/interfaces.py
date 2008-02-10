import zope.interface

class IMarsFormDirectives(zope.interface.Interface):
    """These directives are used with WidgetTemplateFactory"""

    def mode(string):
        """        """

    def view(class_or_interface):
        """        """

    def field(class_or_interface):
        """        """

    def widget(class_or_interface):
        """        """


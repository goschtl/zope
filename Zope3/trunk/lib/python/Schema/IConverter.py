from Interface import Interface

class IConverter(Interface):
    def convert(self, value):
        """Call an IConverter with a value, and it will try to convert to
        another value and return the result. If conversion cannot take
        place, the convertor will raise a ConversionError. (or a
        ValidationError in case of Converters using Schemas inside?)
        """
        pass
    

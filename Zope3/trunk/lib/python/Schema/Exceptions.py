
class StopValidation(Exception):
    pass

class ValidationError(Exception):
    def __init__(self,error_name):
        Exception.__init__(self)
        self.error_name=error_name

    def __cmp__(self,other):
        return cmp(self.error_name, other.error_name)

class ValidationErrorsAll(Exception):
    def __init__(self,list):
        Exception.__init__(self)
        self.errors = list
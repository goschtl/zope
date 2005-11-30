# this is a package

def initialize(context):
    from Products.FiveException.monkey import installExceptionHook
    installExceptionHook()

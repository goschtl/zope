# this is a product which loads an external method

def initialize(context):
    from Products.ExternalMethod.ExternalMethod import ExternalMethod
    em = ExternalMethod('temp', 'temp', 'externalmethod.somemodule',
                        'someExternalMethod')
    return em('external method')




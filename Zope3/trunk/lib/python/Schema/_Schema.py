
def validate(schema, values):
    """Pass in field values in dictionary and validate whether they
    conform to schema. Return validated values.
    """
    from IField import IField
    result = {}
    for name in schema.names(1):
        attr = schema.getDescriptionFor(name)
        if IField.isImplementedBy(attr):
            result[name] = attr.validate(values.get(name))
    return result
    
# Now we can create the interesting interfaces and wire them up:
def wire():

    from Interface.Implements import implements

    from IField import IField
    from _Field import Field
    implements(Field, IField, 0)
    
    from IField import IBool
    from _Field import Bool
    implements(Bool, IBool, 0)

    from IField import IStr
    from _Field import Str
    implements(Str, IStr, 0)

    from IField import IInt
    from _Field import Int
    implements(Int, IInt, 0)

    
wire()
del wire 


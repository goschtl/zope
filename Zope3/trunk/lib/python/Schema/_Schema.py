from Schema.Exceptions import StopValidation, ValidationError, ValidationErrorsAll

def validateMapping(schema, values):
    """Pass in field values in mapping and validate whether they
    conform to schema. Stop at first error.
    """
    from IField import IField
    for name in schema.names(1):
        attr = schema.getDescriptionFor(name)
        if IField.isImplementedBy(attr):
            attr.validate(values.get(name))


def validateMappingAll(schema, values):
    """Pass in field values in mapping and validate whether they
    conform to schema.
    """
    list=[]
    from IField import IField
    for name in schema.names(1):
        attr = schema.getDescriptionFor(name)
        if IField.isImplementedBy(attr):
            try:
                attr.validate(values.get(name))
            except ValidationError, e:
                list.append((name, e))
    if list:
        raise ValidationErrorsAll, list

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


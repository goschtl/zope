from Interface import Interface

import _Field as Field

class IField(Interface):
    """All fields conform to this schema. Note that the interpretation
    of 'required' is up to each field by itself. For some fields, such as
    IBoolean, requiredness settings may make no difference.
    """

    title = Field.Str(
        title="Title",
        description="Title.",
        default=""
        )
    
    description = Field.Str(
        title="Description",
        description="Description.",
        default="",
        required=0)

    readonly = Field.Bool(
        title="Read Only",
        description="Read-only.",
        default=0)
    
    required = Field.Bool(
        title="Required",
        description="Required.",
        default=1)
    
class IBool(IField):
    default = Field.Bool(
        title="Default",
        description="Default.",
        default=0)

class IStr(IField):

    default = Field.Str(
        title="Default",
        description="Default.",
        default="")
    
    # whitespace = Field.Selection(
    #     title="Whitespace",
    #     description="preserve: whitespace is preserved."
    #                 "replace: all occurences of tab, line feed and "
    #                 "carriage return are replaced with space characters. "
     #                 "collapse: first process as in 'replace', then "
    #                 "collapse all spaces to a single space, and strip any "
    #                 "spaces from front and back."
    #                 "strip: strip off whitespace from front and back.",
    #     items=[("preserve", "preserve"),
    #            ("replace", "replace"),
    #            ("collapse", "collapse"),
    #            ("strip", "strip")],
    #     selection_type=IStr,
    #     default="strip")

    min_length = Field.Int(
        title="Minimum length",
        description=("Value after whitespace processing cannot have less than "
                     "min_length characters. If min_length is None, there is "
                     "no minimum."),
        required=0,
        min=0, # needs to be a positive number
        default=0)

    max_length = Field.Int(
        title="Maximum length",
        description=("Value after whitespace processing cannot have greater "
                     "or equal than max_length characters. If max_length is None, "
                     "there is no maximum."),
        required=0,
        min=0, # needs to be a positive number
        default=None)

##     pattern = Str(
##         title="Pattern",
##         description="A regular expression by which the value "
##                     "(after whitespace processing) should be constrained."
##                     "If None, no pattern checking is performed.",
        
##         default=None,
##         required=0)
    
class IInt(IField):
    default = Field.Int(
        title="Default",
        description="Default.",
        default=0)
    
    min = Field.Int(
        title="Minimum",
        description="Value after whitespace processing cannot have less than "
                    "min characters. If min is None, there is no minimum.",
        required=0,
        min=0,
        default=0)

    max = Field.Int(
        title="Maximum",
        description="Value after whitespace processing cannot have greater or "
                    "equal than max characters. If max is None, there is no "
                    "maximum.",
        required=0,
        min=0,
        default=None)

##    pattern = Field.Str(
##         title="Pattern",
##         description="A regular expression by which the value "
##                     "(after whitespace processing) should be constrained."
##                     "If None, no pattern checking is performed.",
        
##         default=None,
##         required=0)
    
    

##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Schema interfaces and exceptions

$Id: interfaces.py,v 1.23 2003/06/12 17:27:59 fdrake Exp $
"""
from zope.interface import Interface, Attribute
from zope.i18n import MessageIDFactory

_ = MessageIDFactory("zope")


class StopValidation(Exception):
    """Raised if the validation is completed early.

    Note that this exception should be always caught, since it is just
    a way for the validator to save time.
    """


class ValidationError(Exception):
    """Raised if the Validation process fails."""

    def __cmp__(self, other):
        return cmp(self.args, other.args)

    def __repr__(self):
        return ' '.join(map(str, self.args))

# Delay these imports to avoid circular import problems
from zope.schema._bootstrapfields import Field, Text, TextLine, Bool, Int
from zope.schema._bootstrapfields import Container, Iterable


class IField(Interface):
    """Basic Schema Field Interface.

    Fields are used for Interface specifications.  They at least provide
    a title, description and a default value.  You can also
    specify if they are required and/or readonly.

    The Field Interface is also used for validation and specifying
    constraints.

    We want to make it possible for a IField to not only work
    on its value but also on the object this value is bound to.
    This enables a Field implementation to perform validation
    against an object which also marks a certain place.

    Note that many fields need information about the object
    containing a field. For example, when validating a value to be
    set as an object attribute, it may be necessary for the field to
    introspect the object's state. This means that the field needs to
    have access to the object when performing validation::

         bound = field.bind(object)
         bound.validate(value)

    """

    def bind(object):
        """Return a copy of this field which is bound to context.

        The copy of the Field will have the 'context' attribute set
        to 'object'.  This way a Field can implement more complex
        checks involving the object's location/environment.

        Many fields don't need to be bound. Only fields that condition
        validation or properties on an object containing the field
        need to be bound.
        """

    title = TextLine(
        title=_(u"Title"),
        description=_(u"A short summary or label"),
        default=u"",
        required=False,
        )

    description = Text(
        title=_(u"Description"),
        description=_(u"A description of the field"),
        default=u"",
        required=False,
        )

    required = Bool(
        title=_(u"Required"),
        description=(
        _(u"tells whether a field requires its value to exist.")),
        default=True)

    readonly = Bool(
        title=_(u"Read Only"),
        description=_(u"Read-only."), # XXX what is this?
        required=False,
        default=False)

    default = Field(
        title=_(u"default field value if no value is present"),
        description=_(u"""The field default value may be None or a legal
                        field value""")
        )

    def constraint(value):
        u"""Check a customized contraint on the value.

        You can implement this method with your Field to
        require a certain constraint.  This relaxes the need
        to inherit/subclass a Field you to add a simple contraint.
        Returns true if the given value is within the Field's contraint.
        """

    def validate(value):
        u"""Validate that the given value is a valid field value.

        Returns nothing but raises an error if the value is invalid.
        It checks everything specific to a Field and also checks
        with the additional constraint.
        """

    order = Int(
        title=_(u"Field Order"),
        description=_(u"""\
        The order attribute can be used to determine the order in
        which fields in a schema were defined. If one field is created
        after another (in the same thread), its order will be
        greater.

        (Fields in separate threads could have the same order.)
        """),
        required=True,
        readonly=True,
        )

    def get(object):
        """Get the value of the field for the given object."""

    def query(object, default=None):
        """Query the value of the field for the given object.

        Return the default if the value hasn't been set.
        """

    def set(object, value):
        """Set the value of the field for the object

        Raises a type error if the field is a read-only field.
        """

class IIterable(IField):
    u"""Fields with a value that can be iterated over.

    The value needs to support iteration; the implementation mechanism
    is not constrained.  (Either __iter__() or __getitem__() may be
    used.)
    """

class IContainer(IField):
    u"""Fields whose value allows an 'x in value' check.

    The Value needs to support the 'in' operator, but is not
    constrained in how it does so (whether it defines __contains__()
    or __getitem__() is immaterial).
    """

class IOrderable(IField):
    u"""Field requiring its value to be orderable.

    The set of value needs support a complete ordering; the
    implementation mechanism is not constrained.  Either __cmp__() or
    'rich comparison' methods may be used.
    """

class ILen(IField):
    u"""A Field requiring its value to have a length.

    The value needs to have a conventional __len__ method.
    """

class IMinMax(IOrderable):
    u"""Field requiring its value to be between min and max.

    This implies that the value needs to support the IOrderable interface.
    """

    min = Field(
        title=_(u"Start of the range"),
        required=False,
        default=None
        )

    max = Field(
        title=_(u"End of the range (excluding the value itself)"),
        required=False,
        default=None
        )


class IMinMaxLen(ILen):
    u"""Field requiring the length of its value to be within a range"""

    min_length = Int(
        title=_(u"Minimum length"),
        description=_(u"""\
        Value after whitespace processing cannot have less than
        min_length characters. If min_length is None, there is
        no minimum.
        """),
        required=False,
        min=0, # needs to be a positive number
        default=0)

    max_length = Int(
        title=_(u"Maximum length"),
        description=_(u"""\
        Value after whitespace processing cannot have greater
        or equal than max_length characters. If max_length is
        None, there is no maximum."""),
        required=False,
        min=0, # needs to be a positive number
        default=None)

class IEnumerated(IField):
    u"""Field whose value is contained in a predefined set"""

    allowed_values = Container(
        title=_(u"Allowed Values"),
        description=_(u"""\
        Only values specified here can be values of this field.
        If the list is empty, then there are no further
        restictions."""),
        required=False)

IValueSet = IEnumerated

class IInterfaceField(IField):
    u"""Fields with a value that is an interface (implementing
    zope.interface.Interface)."""

class IBool(IField):
    u"""Boolean Field."""

class IBytes(IMinMaxLen, IEnumerated, IIterable, IField):
    # XXX IEnumerated will be removed in the future.
    u"""Field containing a byte string (like the python str).

    The value might be contrained to be with length limits.
    """

class IBytesLine(IBytes):
    u"""Field containing a byte string without newlines."""

class IText(IMinMaxLen, IEnumerated, IIterable, IField):
    # XXX IEnumerated doesn't make sense for multi-line strings, so will
    # be removed in the future.
    u"""Field containing a unicode string."""

class ISourceText(IText):
    u"""Field for source text of object."""

class ITextLine(IText):
    u"""Field containing a unicode string without newlines."""

class IEnumeratedTextLine(IEnumerated, ITextLine):
    u"""Field containing a unicode string without newlines.

    The value may be constrained to an element of a specified list.
    """

class IPassword(ITextLine):
    u"""Field containing a unicode string without newlines that is a password."""

class IInt(IMinMax, IEnumerated, IField):
    # XXX IEnumerated will be removed; use IEnumeratedInt instead if you
    # need the IEnumerated interface.
    u"""Field containing an Integer Value."""

class IEnumeratedInt(IInt, IEnumerated):
    u"""Field containing an Integer Value.

    The value may be constrained to an element of a specified list.
    """

class IFloat(IMinMax, IEnumerated, IField):
    # XXX IEnumerated will be removed; use IEnumeratedFloat instead if you
    # need the IEnumerated interface.
    u"""Field containing a Float."""

class IEnumeratedFloat(IEnumerated, IFloat):
    u"""Field containing a Float.

    The value may be constrained to an element of a specified list.
    """

class IDatetime(IMinMax, IEnumerated, IField):
    # XXX IEnumerated will be removed; use IEnumeratedDatetime instead
    # if you need the IEnumerated interface.
    u"""Field containing a DateTime."""

class IEnumeratedDatetime(IEnumerated, IDatetime):
    u"""Field containing a DateTime.

    The value may be constrained to an element of a specified list.
    """

def _fields(values):
    for value in values:
        if not IField.isImplementedBy(value):
            return False
    return True

class ISequence(IMinMaxLen, IIterable, IContainer):
    u"""Field containing a Sequence value.

    The Value must be iterable and may have a min_length/max_length.
    """

    value_types = Iterable(
        title=_(u"Value Types"),
        description=(
        _(u"""\
        If set to a non-empty value, field value items must conform to one
        of the given types, which are expressed via fields.
        """)),
        required=False,
        constraint=_fields,
        )

class ITuple(ISequence):
    u"""Field containing a conventional tuple."""

class IList(ISequence):
    u"""Field containing a conventional list."""

class IDict(IMinMaxLen, IIterable, IContainer):
    u"""Field containing a conventional dict.

    The key_types and value_types field allow specification
    of restrictions for keys and values contained in the dict.
    """

    key_types = Iterable(
        title=_(u"Value Types"),
        description=_(u"""\
        If set to a non-empty value, field value keys must conform to one
        of the given types, which are expressed via fields.
        """),
        constraint=_fields,
        required=False,
        )

    value_types = Iterable(
        title=_(u"Value Types"),
        description=(
        _(u"""\
        If set to a non-empty value, field value values must conform to one
        of the given types, which are expressed via fields.
        """)),
        constraint=_fields,
        required=False,
        )


class IVocabularyQuery(Interface):
    """Query object for a vocabulary.

    This is a marker interface for query objects; specific
    implementations must derive a more specific interface and
    implement that.  Widget views should be registered for the
    specific interface.
    """

    vocabulary = Attribute("vocabulary",
                           """The source vocabulary for this query object.

                           This needs to be available for use by the
                           query view.
                           """)

class IIterableVocabularyQuery(IVocabularyQuery):
    """Marker interface for a query for a vocabulary that is iterable
    but does not support a specialized query interface."""


class ITerm(Interface):
    """Object representing a single value in a vocabulary."""

    value = Attribute(
        "value", "The value used to represent vocabulary term in a field.")


class ITokenizedTerm(ITerm):
    """Object representing a single value in a tokenized vocabulary.
    """

    token = Attribute(
        "token",
        """Token which can be used to represent the value on a stream.

        The value of this attribute must be a non-empty 7-bit string.
        Control characters are not allowed.
        """)


class IBaseVocabulary(Interface):
    """Representation of a vocabulary.

    At this most basic level, a vocabulary only need to support a test
    for containment.  This can be implemented either by __contains__()
    or by sequence __getitem__() (the later only being useful for
    vocabularies which are intrinsically ordered).
    """

    def getQuery():
        """Return an IVocabularyQuery object for this vocabulary.

        Vocabularies which do not support query must return None.
        """

    def getTerm(value):
        """Return the ITerm object for the term 'value'.

        If 'value' is not a valid term, this method raises LookupError.
        """

class IIterableVocabulary(Interface):
    """Vocabulary which supports iteration over allowed values.

    The objects iteration provides must conform to the ITerm
    interface.
    """

    def __iter__():
        """Return an iterator which provides the terms from the vocabulary."""

    def __len__():
        """Return the number of valid terms, or sys.maxint."""


class ISubsetVocabulary(Interface):
    """Vocabulary which represents a subset of another vocabulary."""

    def getMasterVocabulary():
        """Returns the vocabulary that this is a subset of."""


class IVocabulary(IIterableVocabulary, IBaseVocabulary):
    """Vocabulary which is iterable."""


class IVocabularyTokenized(Interface):
    """Vocabulary that provides support for tokenized representation.

    This interface must be used as a mix-in with IBaseVocabulary.

    Terms returned from getTerm() and provided by iteration must
    conform to ITokenizedTerm.
    """

    def getTermByToken(token):
        """Return an ITokenizedTerm for the passed-in token."""


class IVocabularyFieldMixin(Interface):
    # Mix-in interface that defines interesting things common to all
    # vocabulary fields.

    vocabularyName = TextLine(
        title=u"Vocabulary Name",
        description=(u"The name of the vocabulary to be used.  This name\n"
                     u"is intended to be used by the IVocabularyRegistry's\n"
                     u"get() method."),
        required=False,
        default=None)

    vocabulary = Attribute(
        "vocabulary",
        ("IBaseVocabulary to be used, or None.\n"
         "\n"
         "If None, the vocabularyName should be used by an\n"
         "IVocabularyRegistry should be used to locate an appropriate\n"
         "IBaseVocabulary object."))


class IVocabularyField(IVocabularyFieldMixin, IField):
    """Field with a vocabulary-supported value.

    The value for fields of this type is a single value from the
    vocabulary.
    """


class IVocabularyMultiField(IVocabularyFieldMixin, IMinMaxLen, IField):
    # XXX This is really a base class used in the more specific
    # IVocabulary*Field interfaces.
    """Field with a value containing selections from a vocabulary..

    The value for fields of this type need to support at least
    containment checks using 'in' and iteration.

    The length constraint provided by IMinMaxLen constrains the number
    of elements in the value.
    """


class IVocabularyBagField(IVocabularyMultiField):
    """Field representing an unordered collection of values from a
    vocabulary.

    Specific values may be represented more than once.
    """

class IVocabularyListField(IVocabularyMultiField):
    """Field representing an ordered collection of values from a
    vocabulary.

    Specific values may be represented more than once.
    """

class IVocabularySetField(IVocabularyMultiField):
    """Field representing an unordered collection of values from a
    vocabulary.

    Specific values may be represented at most once.
    """

class IVocabularyUniqueListField(IVocabularyMultiField):
    """Field representing an ordered collection of values from a
    vocabulary.

    Specific values may be represented at most once.
    """


class IVocabularyRegistry(Interface):
    """Registry that provides IBaseVocabulary objects for specific fields.
    """

    def get(object, name):
        """Return the vocabulary named 'name' for the content object
        'object'.

        When the vocabulary cannot be found, LookupError is raised.
        """

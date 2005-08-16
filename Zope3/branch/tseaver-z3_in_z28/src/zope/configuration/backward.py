##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Pre-zcml-geddon backward compatability

Rather than revisit all of the old meta configurations, we'll
support the old configurations for a time until they can be converted.
There are two aspects of this:

1. Supporting complex directives (as opposed to simple and grouping
   directives). This support is actually provided in config.py.
   We'll probably support complex directives indefinately, as there
   are some pretty complicated handlers in place now that we don't
   want to take time to rewrite any time soon.

2. Supporting the old-style meta-configuration ZCML directives:
   zope:directives, zope:directive, zope:description, and
   zope:attribute.  Hopefully, we can get rid of these sooner by
   converting the existing meta configurations to use the new
   meta: directives and schema. Certainly directives with message ids
   will need to be converted.

This file contains the implementations of the old-style meta
configurations.

$Id$
"""

from keyword import iskeyword
from zope.configuration import config
from zope import interface
from zope import schema


class IDescribed(interface.Interface):

    name = schema.TextLine(
        title=u"Directive name",
        description=u"The name of the directive being defined"
        )

    description = schema.Text(
        title=u"Directive discription",
        description=u"This should document how the directive is used.",
        default=u"",
        )

class ISubdirectiveInfo(IDescribed):
    """Information common to all directive definitions have
    """

    attributes = schema.Bytes(
        title=u"Attribute names",
        description=u"This is a space-speratated list of attribute names. "
                    u"This is used to provide a mimimal specification the "
                    u"attributes used.",
        default="",
        )

class IDirectiveInfo(ISubdirectiveInfo):
    """Information common to all directive definitions have
    """
    
    handler = config.fields.GlobalObject(
        title=u"Directive handler",
        description=u"The dotted name of the directive handler",
        )

class ISubdirectiveContext(ISubdirectiveInfo, config.IConfigurationContext):
    pass

class IDirectiveContext(IDirectiveInfo, ISubdirectiveContext):
    pass


class Described:

    interface.implements(IDescribed)

    description = u''
            
    def _merge_description_and_info(self):
        r"""Combind a description, given as an attribute with info text

        >>> d = Described()
        >>> d.info = Described() # Any object with attributes will do
        >>> d.info.text = u''
        >>> d._merge_description_and_info()
        >>> d.info.text
        u''

        >>> d.info.text = u'   \n  '
        >>> d._merge_description_and_info()
        >>> d.info.text
        u'   \n  '

        >>> d.description = u'test directive'
        >>> d._merge_description_and_info()
        >>> d.info.text
        u'test directive'

        >>> d.info.text = u'blah\nblah'
        >>> d._merge_description_and_info()
        >>> d.info.text
        u'test directive\n\nblah\nblah'
        
        """
        if self.description:
            if self.info.text.strip():
                self.info.text = self.description + u"\n\n" + self.info.text
            else:
                self.info.text = self.description

class Attributed(config.GroupingContextDecorator):
    """Compute schema definitions from simple attribute specifications

    The attribute specifications can be given as simple names in the
    constructor:

    >>> context = config.ConfigurationMachine()
    >>> x = Attributed(context, attributes=u"a b c")

    Or the can be provides as keys added to the attributes disctionary:

    >>> x.attributes['foo'] = schema.Int(title=u"Foo")

    When tha _schema_from_attrs method is called, a schema is computed:

    >>> x._schema_from_attrs()
    >>> for name in x.schema:
    ...   f = x.schema[name]
    ...   print f.__class__.__name__, f.__name__, f.title, int(f.required)
    Text a a 0
    Text c c 0
    Text b b 0
    Int foo Foo 1

    If you need to be able to accept arbritrary parameters, include an
    attribute named "*" in the list of attributes:

    >>> context = config.ConfigurationMachine()
    >>> x = Attributed(context, attributes=u"a b c *")
    >>> x._schema_from_attrs()
    >>> for name in x.schema:
    ...   f = x.schema[name]
    ...   print f.__class__.__name__, f.__name__, f.title, int(f.required)
    Text a a 0
    Text c c 0
    Text b b 0

    Note that we don't see "*" in the schema. Rather, we see that the
    schema as a tagged value:

    >>> x.schema.getTaggedValue("keyword_arguments")
    1

    Indicating that the directive handler accepts extra keyword
    arguments, which means that arbitrary extra parameters can be given.
    """

    interface.implementsOnly(IDescribed)

    __keyword_arguments = False

    def attribute(self, name, required=False, description=u''):
        if name == '*':
            self.__keyword_arguments = True
            return
        
        aname = str(name)
        if iskeyword(name):
            aname += '_'
        self.attributes[aname] = schema.Text(
            title = unicode(aname),
            required = required,
            description = description,
            )

    def __init__(self, context, attributes=u'', **kw):
        config.GroupingContextDecorator.__init__(self, context, **kw)
        self.attributes = {}
        for name in attributes.strip().split():
            self.attribute(name)

    def _schema_from_attrs(self):
        schema = interface.Interface.__class__(
            "schema generated from attributes",
            (interface.Interface, ),
            self.attributes,
            )
        if not self.attributes:
            # No attribute definitions, allow keyword args
            schema.setTaggedValue('keyword_arguments', True)
        self.schema = schema

        if self.__keyword_arguments:
            schema.setTaggedValue('keyword_arguments', True)
    

class Directive(Attributed, Described):
    """Handler for the directive directive

    Actual definition of the directive is delayed until
    sub(meta)directives have been handled.

    See the test in tests/test_backward
    """
    interface.implements(IDirectiveContext)
    usedIn = config.IConfigurationContext

    def __init__(self, context, **kw):
        Attributed.__init__(self, context, **kw)
        self.subdirectives = {}

    def after(self):
        self._schema_from_attrs()
        self._merge_description_and_info()
        if self.subdirectives:
            # we have subdirectives, so set up a complex directive
            complex = config.ComplexDirectiveDefinition(self)
            complex.handler = self.handler
            complex.update(self.subdirectives)
            complex.before()
        else:
            config.defineSimpleDirective(self, self.name, self.schema,
                                         self.handler, self.namespace)


class Subdirective(Attributed, Described):
    """Handler for the directive directive

    Actual definition of the directive is delayed until
    sub(meta)directives have been handled.

    >>> context = config.ConfigurationMachine()
    >>> d = Directive(context)
    >>> len(d.subdirectives)
    0
    >>> s = Subdirective(d, name="foo", attributes=u"a b")
    >>> len(d.subdirectives)
    0
    >>> class Info:
    ...    text=u'spam'
    >>> s.info = Info()
    >>> s.after()
    >>> len(d.subdirectives)
    1
    >>> schema, info = d.subdirectives['foo']

    >>> def sorted(x):
    ...     r = list(x)
    ...     r.sort()
    ...     return r

    >>> sorted(schema)
    ['a', 'b']
    >>> info.text
    u'spam'

    """

    interface.implements(ISubdirectiveContext)

    def after(self):
        self._schema_from_attrs()
        self._merge_description_and_info()
        self.context.subdirectives[self.name] = self.schema, self.info

class IAttribute(IDescribed):

    required = config.fields.Bool(
        title=u"Required",
        description=u"Is the attribute required?",
        required=True,
        default=False,
        )

class Attribute(config.GroupingContextDecorator, Described):
    r"""Simple attribute specification

    Provide a very simple specification of an attribute and add it to
    the attributes dictionary of the containing context.

    >>> context = config.ConfigurationMachine()
    >>> d = Directive(context, attributes=u"a")
    >>> len(d.attributes)
    1

    >>> a = Attribute(d, name="a", description=u"blah")
    >>> class Info:
    ...    text=u'spam'
    >>> a.info = Info()
    >>> d.attributes['a'].description
    u''
    >>> a.after()
    >>> d.attributes['a'].description
    u'blah\n\nspam'
    >>> d.attributes['a'].required
    0
    >>> d.attributes['a'].__class__.__name__
    'Text'

    >>> a = Attribute(d, name="b", description=u"eek", required=True)
    >>> class Info:
    ...    text=u'spam'
    >>> a.info = Info()
    >>> a.after()
    >>> d.attributes['b'].description
    u'eek\n\nspam'
    >>> d.attributes['b'].required
    1

    >>> len(d.attributes)
    2
    
    """

    required = False

    def after(self):
        self._merge_description_and_info()
        self.context.attribute(self.name, self.required, self.info.text)

class Description(config.GroupingContextDecorator):
    r"""Provide descriptions for surrounding directives

    This works a bit hard to be an effective noop, since
    it has the same effect as providing text data.

    >>> context = config.ConfigurationMachine()
    >>> d = Directive(context, attributes=u"a")
    >>> class Info:
    ...    text=u'spam         \n'
    >>> d.info = Info()

    >>> des = Description(d)
    >>> des.info = Info()
    >>> des.info.text = u"blah\nblah"
    >>> des.after()

    >>> d.info.text
    u'spam\n\nblah\nblah'
    
    """
    
    def after(self):
        """Merge our info with containing directive's info
        """

        if not self.info.text.strip():
            return

        context = self.context
        old = context.info.text.rstrip()
        
        if old:
            context.info.text = old + u"\n\n" + self.info.text
        else:
            context.info.text += self.info.text


def bootstrap(context):

    # zope:directives
    context((config.metans, 'groupingDirective'),
            name='directives',
            namespace=config.zopens,
            handler="zope.configuration.config.DirectivesHandler",
            schema="zope.configuration.config.IDirectivesInfo"
            )

    # zope:directive
    context((config.metans, 'groupingDirective'),
            name='directive',
            namespace=config.zopens,
            usedIn="zope.configuration.config.IDirectivesContext",
            handler="zope.configuration.backward.Directive",
            schema="zope.configuration.backward.IDirectiveInfo"
            )

    # zope:subdirective
    context((config.metans, 'groupingDirective'),
            name='subdirective',
            namespace=config.zopens,
            usedIn="zope.configuration.backward.IDirectiveContext",
            handler="zope.configuration.backward.Subdirective",
            schema="zope.configuration.backward.ISubdirectiveInfo"
            )

    # zope:attribute
    context((config.metans, 'groupingDirective'),
            name='attribute',
            namespace=config.zopens,
            usedIn="zope.configuration.backward.ISubdirectiveContext",
            handler="zope.configuration.backward.Attribute",
            schema="zope.configuration.backward.IAttribute"
            )

    # zope:discription
    context((config.metans, 'groupingDirective'),
            name='description',
            namespace=config.zopens,
            usedIn="zope.configuration.backward.IDescribed",
            handler="zope.configuration.backward.Description",
            schema="zope.interface.Interface"
            )

    

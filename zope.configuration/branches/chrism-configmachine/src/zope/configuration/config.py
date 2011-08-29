##############################################################################
#
# Copyright (c) 2011 Zope Foundation and Contributors.
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
"""Configuration processor

See README.txt
"""

__docformat__ = 'restructuredtext'

from keyword import iskeyword
import sys

import zope.schema

from zope.interface import Interface
from zope.interface import implements
from zope.configuration import fields

from zope.configmachine import GroupingContextDecorator
from zope.configmachine import RootStackItem
from zope.configmachine.exceptions import ConfigurationError
from zope.configmachine.interfaces import IConfigurationContext
from zope.configmachine.interfaces import IStackItem

zopens = 'http://namespaces.zope.org/zope'
metans = 'http://namespaces.zope.org/meta'
testns = 'http://namespaces.zope.org/test'

##############################################################################
# Bw compat imports

from zope.configmachine.exceptions import ConfigurationExecutionError
from zope.configmachine.exceptions import ConfigurationConflictError
from zope.configmachine import ConfigurationContext
from zope.configmachine import ConfigurationAdapterRegistry
from zope.configmachine import RootStackItem
from zope.configmachine import expand_action
from zope.configmachine import resolveConflicts

##############################################################################
# Redefinitions

from zope.configmachine import ConfigurationMachine as _ConfigurationMachine

class ConfigurationMachine(_ConfigurationMachine):
    """Configuration machine

    Example:

    >>> machine = ConfigurationMachine()
    >>> ns = "http://www.zope.org/testing"

    Register a directive:

    >>> machine((metans, "directive"),
    ...         namespace=ns, name="simple",
    ...         schema="zope.configuration.tests.directives.ISimple",
    ...         handler="zope.configuration.tests.directives.simple")

    and try it out:

    >>> machine((ns, "simple"), a=u"aa", c=u"cc")

    >>> machine.actions
    [(('simple', u'aa', u'xxx', 'cc'), f, (u'aa', u'xxx', 'cc'))]

    A more extensive example can be found in the unit tests.
    """
    def __init__(self):
        # the base configuration machine does not bootstrap any directives
        super(ConfigurationMachine, self).__init__()
        bootstrap(self)

##############################################################################
# Stack items

class SimpleStackItem(object):
    """Simple stack item

    A simple stack item can't have anything added after it.  It can
    only be removed.  It is used for simple directives and
    subdirectives, which can't contain other directives.

    It also defers any computation until the end of the directive
    has been reached.
    """

    implements(IStackItem)

    def __init__(self, context, handler, info, *argdata):
        newcontext = GroupingContextDecorator(context)
        newcontext.info = info
        self.context = newcontext
        self.handler = handler
        self.argdata = argdata

    def contained(self, name, data, info):
        raise ConfigurationError("Invalid directive %s" % str(name))

    def finish(self):
        # We're going to use the context that was passed to us, which wasn't
        # created for the directive.  We want to set it's info to the one
        # passed to us while we make the call, so we'll save the old one
        # and restore it.
        context = self.context
        args = toargs(context, *self.argdata)
        actions = self.handler(context, **args)
        if actions:
            # we allow the handler to return nothing
            for action in actions:
                context.action(*action)


class GroupingStackItem(RootStackItem):
    """Stack item for a grouping directive

    A grouping stack item is in the stack when a grouping directive is
    being processed.  Grouping directives group other directives.
    Often, they just manage common data, but they may also take
    actions, either before or after contained directives are executed.

    A grouping stack item is created with a grouping directive
    definition, a configuration context, and directive data.

    To see how this works, let's look at an example:

    We need a context. We'll just use a configuration machine

    >>> context = ConfigurationMachine()

    We need a callable to use in configuration actions.  We'll use a
    convenient one from the tests:

    >>> from zope.configuration.tests.directives import f

    We need a handler for the grouping directive. This is a class
    that implements a context decorator.  The decorator must also
    provide ``before`` and ``after`` methods that are called before
    and after any contained directives are processed.  We'll typically
    subclass ``GroupingContextDecorator``, which provides context
    decoration, and default ``before`` and ``after`` methods.


    >>> class SampleGrouping(GroupingContextDecorator):
    ...    def before(self):
    ...       self.action(('before', self.x, self.y), f)
    ...    def after(self):
    ...       self.action(('after'), f)

    We'll use our decorator to decorate our initial context, providing
    keyword arguments x and y:

    >>> dec = SampleGrouping(context, x=1, y=2)

    Note that the keyword arguments are made attributes of the
    decorator.

    Now we'll create the stack item.

    >>> item = GroupingStackItem(dec)

    We still haven't called the before action yet, which we can verify
    by looking at the context actions:

    >>> context.actions
    []

    Subdirectives will get looked up as adapters of the context.

    We'll create a simple handler:

    >>> def simple(context, data, info):
    ...     context.action(("simple", context.x, context.y, data), f)
    ...     return info

    and register it with the context:

    >>> context.register(IConfigurationContext, (testns, 'simple'), simple)

    This handler isn't really a propert handler, because it doesn't
    return a new context.  It will do for this example.

    Now we'll call the contained method on the stack item:

    >>> item.contained((testns, 'simple'), {'z': 'zope'}, "someinfo")
    'someinfo'

    We can verify thet the simple method was called by looking at the
    context actions. Note that the before method was called before
    handling the contained directive.

    >>> from pprint import PrettyPrinter
    >>> pprint=PrettyPrinter(width=60).pprint

    >>> pprint(context.actions)
    [(('before', 1, 2), f),
     (('simple', 1, 2, {'z': 'zope'}), f)]

    Finally, we call finish, which calls the decorator after method:

    >>> item.finish()

    >>> pprint(context.actions)
    [(('before', 1, 2), f),
     (('simple', 1, 2, {'z': 'zope'}), f),
     ('after', f)]


    If there were no nested directives:

    >>> context = ConfigurationMachine()
    >>> dec = SampleGrouping(context, x=1, y=2)
    >>> item = GroupingStackItem(dec)
    >>> item.finish()

    Then before will be when we call finish:

    >>> pprint(context.actions)
    [(('before', 1, 2), f), ('after', f)]

    """

    implements(IStackItem)

    def __init__(self, context):
        super(GroupingStackItem, self).__init__(context)

    def __callBefore(self):
        actions = self.context.before()
        if actions:
            for action in actions:
                self.context.action(*action)
        self.__callBefore = noop

    def contained(self, name, data, info):
        self.__callBefore()
        return RootStackItem.contained(self, name, data, info)

    def finish(self):
        self.__callBefore()
        actions = self.context.after()
        if actions:
            for action in actions:
                self.context.action(*action)

def noop():
    pass


class ComplexStackItem(object):
    """Complex stack item

    A complex stack item is in the stack when a complex directive is
    being processed.  It only allows subdirectives to be used.

    A complex stack item is created with a complex directive
    definition (IComplexDirectiveContext), a configuration context,
    and directive data.

    To see how this works, let's look at an example:

    We need a context. We'll just use a configuration machine

    >>> context = ConfigurationMachine()

    We need a callable to use in configuration actions.  We'll use a
    convenient one from the tests:

    >>> from zope.configuration.tests.directives import f

    We need a handler for the complex directive. This is a class
    with a method for each subdirective:

    >>> class Handler(object):
    ...   def __init__(self, context, x, y):
    ...      self.context, self.x, self.y = context, x, y
    ...      context.action('init', f)
    ...   def sub(self, context, a, b):
    ...      context.action(('sub', a, b), f)
    ...   def __call__(self):
    ...      self.context.action(('call', self.x, self.y), f)

    We need a complex directive definition:

    >>> class Ixy(Interface):
    ...    x = zope.schema.TextLine()
    ...    y = zope.schema.TextLine()
    >>> definition = ComplexDirectiveDefinition(
    ...        context, name="test", schema=Ixy,
    ...        handler=Handler)
    >>> class Iab(Interface):
    ...    a = zope.schema.TextLine()
    ...    b = zope.schema.TextLine()
    >>> definition['sub'] = Iab, ''

    OK, now that we have the context, handler and definition, we're
    ready to use a stack item.

    >>> item = ComplexStackItem(definition, context, {'x': u'xv', 'y': u'yv'},
    ...                         'foo')

    When we created the definition, the handler (factory) was called.

    >>> context.actions
    [('init', f, (), {}, (), 'foo')]

    If a subdirective is provided, the ``contained`` method of the stack item
    is called. It will lookup the subdirective schema and call the
    corresponding method on the handler instance:

    >>> simple = item.contained(('somenamespace', 'sub'),
    ...                         {'a': u'av', 'b': u'bv'}, 'baz')
    >>> simple.finish()

    Note that the name passed to ``contained`` is a 2-part name, consisting of
    a namespace and a name within the namespace.

    >>> from pprint import PrettyPrinter
    >>> pprint=PrettyPrinter(width=60).pprint

    >>> pprint(context.actions)
    [('init', f, (), {}, (), 'foo'),
     (('sub', u'av', u'bv'), f, (), {}, (), 'baz')]

    The new stack item returned by contained is one that doesn't allow
    any more subdirectives,

    When all of the subdirectives have been provided, the ``finish``
    method is called:

    >>> item.finish()

    The stack item will call the handler if it is callable.

    >>> pprint(context.actions)
    [('init', f, (), {}, (), 'foo'),
     (('sub', u'av', u'bv'), f, (), {}, (), 'baz'),
     (('call', u'xv', u'yv'), f, (), {}, (), 'foo')]


    """

    implements(IStackItem)

    def __init__(self, meta, context, data, info):
        newcontext = GroupingContextDecorator(context)
        newcontext.info = info
        self.context = newcontext
        self.meta = meta

        # Call the handler contructor
        args = toargs(newcontext, meta.schema, data)
        self.handler = self.meta.handler(newcontext, **args)

    def contained(self, name, data, info):
        """Handle a subdirective
        """

        # Look up the subdirective meta data on our meta object
        ns, name = name
        schema = self.meta.get(name)
        if schema is None:
            raise ConfigurationError("Invalid directive", name)
        schema = schema[0] # strip off info
        handler = getattr(self.handler, name)
        return SimpleStackItem(self.context, handler, info, schema, data)

    def finish(self):

        # when we're done, we call the handler, which might return more actions

        # Need to save and restore old info

        try:
            actions = self.handler()
        except AttributeError, v:
            if v[0] == '__call__':
                return # noncallable
            raise
        except TypeError:
            return # non callable

        if actions:
            # we allow the handler to return nothing
            for action in actions:
                self.context.action(*action)

def defineGroupingDirective(context, name, schema, handler,
                            namespace='', usedIn=IConfigurationContext):
    """Define a grouping directive

    Define and register a factory that sets up a grouping directive.

    If the namespace is '*', the directive is registered for all namespaces.

    for example:

    >>> context = ConfigurationMachine()
    >>> from zope.configuration.tests.directives import f
    >>> class Ixy(Interface):
    ...    x = zope.schema.TextLine()
    ...    y = zope.schema.TextLine()

    We won't bother creating a special grouping directive class. We'll
    just use GroupingContextDecorator, which simply sets up a grouping
    context that has extra attributes defined by a schema:

    >>> defineGroupingDirective(context, 'g', Ixy,
    ...                         GroupingContextDecorator, testns)

    >>> context.begin((testns, "g"), x=u"vx", y=u"vy")
    >>> context.stack[-1].context.x
    u'vx'
    >>> context.stack[-1].context.y
    u'vy'

    >>> context(('http://www.zope.com/t1', "g"), x=u"vx", y=u"vy")
    Traceback (most recent call last):
    ...
    ConfigurationError: ('Unknown directive', 'http://www.zope.com/t1', 'g')

    >>> context = ConfigurationMachine()
    >>> defineGroupingDirective(context, 'g', Ixy,
    ...                         GroupingContextDecorator, "*")

    >>> context.begin(('http://www.zope.com/t1', "g"), x=u"vx", y=u"vy")
    >>> context.stack[-1].context.x
    u'vx'
    >>> context.stack[-1].context.y
    u'vy'

    """

    namespace = namespace or context.namespace
    if namespace != '*':
        name = namespace, name

    def factory(context, data, info):
        args = toargs(context, schema, data)
        newcontext = handler(context, **args)
        newcontext.info = info
        return GroupingStackItem(newcontext)
    factory.schema = schema

    context.register(usedIn, name, factory)
    context.document(name, schema, usedIn, handler, context.info)


##############################################################################
# Directive-definition

class DirectiveSchema(fields.GlobalInterface):
    """A field that contains a global variable value that must be a schema
    """

class IDirectivesInfo(Interface):
    """Schema for the ``directives`` directive
    """

    namespace = zope.schema.URI(
        title=u"Namespace",
        description=u"The namespace in which directives' names will be defined",
        )

class IDirectivesContext(IDirectivesInfo, IConfigurationContext):
    pass

class DirectivesHandler(GroupingContextDecorator):
    """Handler for the directives directive

    This is just a grouping directive that adds a namespace attribute
    to the normal directive context.

    """
    implements(IDirectivesContext)


class IDirectiveInfo(Interface):
    """Information common to all directive definitions have
    """

    name = zope.schema.TextLine(
        title = u"Directive name",
        description = u"The name of the directive being defined",
        )

    schema = DirectiveSchema(
        title = u"Directive handler",
        description = u"The dotted name of the directive handler",
        )

class IFullInfo(IDirectiveInfo):
    """Information that all top-level directives (not subdirectives) have
    """

    handler = fields.GlobalObject(
        title = u"Directive handler",
        description = u"The dotted name of the directive handler",
        )

    usedIn = fields.GlobalInterface(
        title = u"The directive types the directive can be used in",
        description = (u"The interface of the directives that can contain "
                       u"the directive"
                       ),
        default = IConfigurationContext,
        )

class IStandaloneDirectiveInfo(IDirectivesInfo, IFullInfo):
    """Info for full directives defined outside a directives directives
    """

def defineSimpleDirective(context, name, schema, handler,
                          namespace='', usedIn=IConfigurationContext):
    """Define a simple directive

    Define and register a factory that invokes the simple directive
    and returns a new stack item, which is always the same simple stack item.

    If the namespace is '*', the directive is registered for all namespaces.

    for example:

    >>> context = ConfigurationMachine()
    >>> from zope.configuration.tests.directives import f
    >>> class Ixy(Interface):
    ...    x = zope.schema.TextLine()
    ...    y = zope.schema.TextLine()
    >>> def s(context, x, y):
    ...    context.action(('s', x, y), f)

    >>> defineSimpleDirective(context, 's', Ixy, s, testns)

    >>> context((testns, "s"), x=u"vx", y=u"vy")
    >>> context.actions
    [(('s', u'vx', u'vy'), f)]

    >>> context(('http://www.zope.com/t1', "s"), x=u"vx", y=u"vy")
    Traceback (most recent call last):
    ...
    ConfigurationError: ('Unknown directive', 'http://www.zope.com/t1', 's')

    >>> context = ConfigurationMachine()
    >>> defineSimpleDirective(context, 's', Ixy, s, "*")

    >>> context(('http://www.zope.com/t1', "s"), x=u"vx", y=u"vy")
    >>> context.actions
    [(('s', u'vx', u'vy'), f)]

    """

    namespace = namespace or context.namespace
    if namespace != '*':
        name = namespace, name

    def factory(context, data, info):
        return SimpleStackItem(context, handler, info, schema, data)
    factory.schema = schema

    context.register(usedIn, name, factory)
    context.document(name, schema, usedIn, handler, context.info)

class IComplexDirectiveContext(IFullInfo, IConfigurationContext):
    pass

class ComplexDirectiveDefinition(GroupingContextDecorator, dict):
    """Handler for defining complex directives

    See the description and tests for ComplexStackItem.
    """

    implements(IComplexDirectiveContext)

    def before(self):

        def factory(context, data, info):
            return ComplexStackItem(self, context, data, info)
        factory.schema = self.schema

        self.register(self.usedIn, (self.namespace, self.name), factory)
        self.document((self.namespace, self.name), self.schema, self.usedIn,
                      self.handler, self.info)

def subdirective(context, name, schema):
    context.document((context.namespace, name), schema, context.usedIn,
                     getattr(context.handler, name, context.handler),
                     context.info, context.context)
    context.context[name] = schema, context.info

##############################################################################
# Features

class IProvidesDirectiveInfo(Interface):
    """Information for a <meta:provides> directive"""

    feature = zope.schema.TextLine(
        title = u"Feature name",
        description = u"""The name of the feature being provided

        You can test available features with zcml:condition="have featurename".
        """,
        )

def provides(context, feature):
    """Declare that a feature is provided in context.

    >>> c = ConfigurationContext()
    >>> provides(c, 'apidoc')
    >>> c.hasFeature('apidoc')
    True

    Spaces are not allowed in feature names (this is reserved for providing
    many features with a single directive in the futute).

    >>> provides(c, 'apidoc onlinehelp')
    Traceback (most recent call last):
      ...
    ValueError: Only one feature name allowed

    >>> c.hasFeature('apidoc onlinehelp')
    False

    """
    if len(feature.split()) > 1:
        raise ValueError("Only one feature name allowed")
    context.provideFeature(feature)


##############################################################################
# Argument conversion

def toargs(context, schema, data):
    """Marshal data to an argument dictionary using a schema

    Names that are python keywords have an underscore added as a
    suffix in the schema and in the argument list, but are used
    without the underscore in the data.

    The fields in the schema must all implement IFromUnicode.

    All of the items in the data must have corresponding fields in the
    schema unless the schema has a true tagged value named
    'keyword_arguments'.

    Here's an example:

    >>> from zope import schema

    >>> class schema(Interface):
    ...     in_ = zope.schema.Int(constraint=lambda v: v > 0)
    ...     f = zope.schema.Float()
    ...     n = zope.schema.TextLine(min_length=1, default=u"rob")
    ...     x = zope.schema.BytesLine(required=False)
    ...     u = zope.schema.URI()

    >>> context = ConfigurationMachine()
    >>> from pprint import PrettyPrinter
    >>> pprint=PrettyPrinter(width=50).pprint

    >>> pprint(toargs(context, schema,
    ...        {'in': u'1', 'f': u'1.2', 'n': u'bob', 'x': u'x.y.z',
    ...          'u': u'http://www.zope.org' }))
    {'f': 1.2,
     'in_': 1,
     'n': u'bob',
     'u': 'http://www.zope.org',
     'x': 'x.y.z'}

    If we have extra data, we'll get an error:

    >>> toargs(context, schema,
    ...        {'in': u'1', 'f': u'1.2', 'n': u'bob', 'x': u'x.y.z',
    ...          'u': u'http://www.zope.org', 'a': u'1'})
    Traceback (most recent call last):
    ...
    ConfigurationError: ('Unrecognized parameters:', 'a')

    Unless we set a tagged value to say that extra arguments are ok:

    >>> schema.setTaggedValue('keyword_arguments', True)

    >>> pprint(toargs(context, schema,
    ...        {'in': u'1', 'f': u'1.2', 'n': u'bob', 'x': u'x.y.z',
    ...          'u': u'http://www.zope.org', 'a': u'1'}))
    {'a': u'1',
     'f': 1.2,
     'in_': 1,
     'n': u'bob',
     'u': 'http://www.zope.org',
     'x': 'x.y.z'}


    If we ommit required data we get an error telling us what was omitted:

    >>> pprint(toargs(context, schema,
    ...        {'in': u'1', 'f': u'1.2', 'n': u'bob', 'x': u'x.y.z'}))
    Traceback (most recent call last):
    ...
    ConfigurationError: ('Missing parameter:', 'u')

    Although we can omit not-required data:

    >>> pprint(toargs(context, schema,
    ...        {'in': u'1', 'f': u'1.2', 'n': u'bob',
    ...          'u': u'http://www.zope.org', 'a': u'1'}))
    {'a': u'1',
     'f': 1.2,
     'in_': 1,
     'n': u'bob',
     'u': 'http://www.zope.org'}

    And we can ommit required fields if they have valid defaults
    (defaults that are valid values):


    >>> pprint(toargs(context, schema,
    ...        {'in': u'1', 'f': u'1.2',
    ...          'u': u'http://www.zope.org', 'a': u'1'}))
    {'a': u'1',
     'f': 1.2,
     'in_': 1,
     'n': u'rob',
     'u': 'http://www.zope.org'}

    We also get an error if any data was invalid:

    >>> pprint(toargs(context, schema,
    ...        {'in': u'0', 'f': u'1.2', 'n': u'bob', 'x': u'x.y.z',
    ...          'u': u'http://www.zope.org', 'a': u'1'}))
    Traceback (most recent call last):
    ...
    ConfigurationError: ('Invalid value for', 'in', '0')

    """

    data = dict(data)
    args = {}
    for name, field in schema.namesAndDescriptions(True):
        field = field.bind(context)
        n = name
        if n.endswith('_') and iskeyword(n[:-1]):
            n = n[:-1]

        s = data.get(n, data)
        if s is not data:
            s = unicode(s)
            del data[n]

            try:
                args[str(name)] = field.fromUnicode(s)
            except zope.schema.ValidationError, v:
                raise ConfigurationError(
                    "Invalid value for", n, str(v)), None, sys.exc_info()[2]
        elif field.required:
            # if the default is valid, we can use that:
            default = field.default
            try:
                field.validate(default)
            except zope.schema.ValidationError:
                raise ConfigurationError("Missing parameter:", n)
            args[str(name)] = default

    if data:
        # we had data left over
        try:
            keyword_arguments = schema.getTaggedValue('keyword_arguments')
        except KeyError:
            keyword_arguments = False
        if not keyword_arguments:
            raise ConfigurationError("Unrecognized parameters:", *data)

        for name in data:
            args[str(name)] = data[name]

    return args

##############################################################################
# Bootstrap code


def bootstrap(context):

    # Set enough machinery to register other directives

    # Define the directive (simple directive) directive by calling it's
    # handler directly

    info = 'Manually registered in zope/configuration/config.py'

    context.info = info
    defineSimpleDirective(
        context,
        namespace=metans, name='directive',
        schema=IStandaloneDirectiveInfo,
        handler=defineSimpleDirective)
    context.info = ''

    # OK, now that we have that, we can use the machine to define the
    # other directives. This isn't the easiest way to proceed, but it lets
    # us eat our own dogfood. :)

    # Standalone groupingDirective
    context((metans, 'directive'),
            info,
            name='groupingDirective',
            namespace=metans,
            handler="zope.configuration.config.defineGroupingDirective",
            schema="zope.configuration.config.IStandaloneDirectiveInfo"
            )

    # Now we can use the grouping directive to define the directives directive
    context((metans, 'groupingDirective'),
            info,
            name='directives',
            namespace=metans,
            handler="zope.configuration.config.DirectivesHandler",
            schema="zope.configuration.config.IDirectivesInfo"
            )

    # directive and groupingDirective inside directives
    context((metans, 'directive'),
            info,
            name='directive',
            namespace=metans,
            usedIn="zope.configuration.config.IDirectivesContext",
            handler="zope.configuration.config.defineSimpleDirective",
            schema="zope.configuration.config.IFullInfo"
            )
    context((metans, 'directive'),
            info,
            name='groupingDirective',
            namespace=metans,
            usedIn="zope.configuration.config.IDirectivesContext",
            handler="zope.configuration.config.defineGroupingDirective",
            schema="zope.configuration.config.IFullInfo"
            )

    # Setup complex directive directive, both standalone, and in
    # directives directive
    context((metans, 'groupingDirective'),
            info,
            name='complexDirective',
            namespace=metans,
            handler="zope.configuration.config.ComplexDirectiveDefinition",
            schema="zope.configuration.config.IStandaloneDirectiveInfo"
            )
    context((metans, 'groupingDirective'),
            info,
            name='complexDirective',
            namespace=metans,
            usedIn="zope.configuration.config.IDirectivesContext",
            handler="zope.configuration.config.ComplexDirectiveDefinition",
            schema="zope.configuration.config.IFullInfo"
            )

    # Finally, setup subdirective directive
    context((metans, 'directive'),
            info,
            name='subdirective',
            namespace=metans,
            usedIn="zope.configuration.config.IComplexDirectiveContext",
            handler="zope.configuration.config.subdirective",
            schema="zope.configuration.config.IDirectiveInfo"
            )

    # meta:provides
    context((metans, 'directive'),
            info,
            name='provides',
            namespace=metans,
            handler="zope.configuration.config.provides",
            schema="zope.configuration.config.IProvidesDirectiveInfo"
            )

_bootstrap = bootstrap # bw compat

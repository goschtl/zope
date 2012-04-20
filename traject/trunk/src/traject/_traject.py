import re
from urllib import unquote

from zope.interface import implementedBy, providedBy
from zope.interface.interfaces import ISpecification
from zope.interface.adapter import AdapterRegistry
from zope.interface import Interface

class IStep(Interface):
    pass

class IFactory(Interface):
    pass

class IInverse(Interface):
    pass

class ParseError(Exception):
    """Raised if there is a problem parsing an URL pattern.
    """

class RegistrationError(Exception):
    """Raised if there is a problem registering an URL pattern.
    """

class ResolutionError(Exception):
    """Raised if there was a problem resolving a path.
    """

class LocationError(Exception):
    """Raised if there was a problem reconstructing a location.
    """
    
def parse(pattern_str):
    """Parse an URL pattern.

    Takes a URL pattern string and parses it into a tuple. Pattern
    strings look like this: foo/:bar/baz

    pattern_str - the pattern

    returns the pattern tuple.
    """
    pattern_str = normalize(pattern_str)
    pattern = tuple(pattern_str.split('/'))
    known_variables = set()
    for step in pattern:
        if step[0] == ':':
            if step in known_variables:
                raise ParseError(
                    'URL pattern contains multiple variables with name: %s' %
                    step[1:])
            known_variables.add(step)
    return pattern

def subpatterns(pattern):
    """Decompose a pattern into sub patterns.

    A pattern can be decomposed into a number of sub patterns.
    ('a', 'b', 'c') for instance has the sub patterns ('a',),
    ('a', 'b') and ('a', 'b', 'c').

    pattern - the pattern tuple to decompose.

    returns the sub pattern tuples of this pattern.
    """
    subpattern = []
    result = []
    for step in pattern:
        subpattern.append(step)
        result.append(tuple(subpattern))
    return result

def generalize_pattern(pattern):
    result = []
    for p in pattern:
        if p[0] == ':':
            result.append(':')
        else:
            result.append(p)
    return tuple(result)

def component_name(pattern):
    return '/'.join(generalize_pattern(pattern))
    
def _get_interface(class_or_interface):
    if ISpecification.providedBy(class_or_interface):
        return class_or_interface
    else:
        return implementedBy(class_or_interface)

_dummy = object()

class Patterns(object):
    def __init__(self):
        self._registry = AdapterRegistry()
        self._inverse_registry = AdapterRegistry()
        self._converters = {
            'unicode': convert_unicode,
            'str': convert_str,
            'int': int,
            'unicodelist': convert_unicodelist,
            'strlist': convert_strlist,
            'intlist': convert_intlist,
            }

    def register_converter(self, converter_name, converter_func):
        """Register a converter function for a converter name.

        Type names are the optional bit in a pattern, behind
        a second colon (i.e. :foo_id:int).
        
        "A converter function must raise ValueError if it cannot
        convert to the desired format.
        """
        self._converters[converter_name] = converter_func

    def register(self, class_or_interface, pattern_str, factory):
        interface = _get_interface(class_or_interface)
        pattern = parse(pattern_str)
        sp = subpatterns(pattern)
        for p in sp:
            name = component_name(p)
            if name[-1] == ':':
                value = p[-1][1:]
                if ':' in value:
                    dummy, converter_name = value.split(':')
                    if converter_name not in self._converters:
                        raise RegistrationError(
                            "Could not register %s because no converter "
                            "can be found for variable %s" %
                            ('/'.join(pattern), value))
                prev_value = self._registry.registered(
                    (interface,), IStep, name)
                if prev_value == value:
                    continue
                if prev_value is not None:
                    raise RegistrationError(
                        "Could not register %s because of a conflict "
                        "between variable %s and already registered %s" %
                        ('/'.join(pattern), value, prev_value))
            else:
                value = _dummy
            self._registry.register((interface,), IStep, name, value)
        p = sp[-1]
        name = component_name(p)
        self._registry.register((interface,), IFactory, name, factory)

    def register_inverse(self,
                         root_class_or_interface, model_class_or_interface,
                         pattern_str, inverse):
        
        self._inverse_registry.register(
            (_get_interface(root_class_or_interface),
             _get_interface(model_class_or_interface)),
            IInverse, u'',
            (parse(pattern_str), inverse))
    
    def resolve(self, root, path, default_factory):
        path = normalize(path)
        names = path.split('/')
        names.reverse()
        return self.resolve_stack(root, names, default_factory)

    def resolve_stack(self, root, stack, default_factory):
        unconsumed, consumed, obj = self.consume_stack(root, stack, default_factory)
        if unconsumed:
            raise ResolutionError(
                "Could not resolve path: %s" % '/'.join(reversed(stack)))
        return obj

    def consume(self, root, path, default_factory):
        path = normalize(path)
        names = path.split('/')
        names.reverse()
        return self.consume_stack(root, names, default_factory)

    def consume_stack(self, root, stack, default_factory):
        variables = {}
        provided = (providedBy(root),)
        obj = root
        pattern = ()
        consumed = []
        while stack:
            name = stack.pop()
            step_pattern = pattern + (name,)
            step_pattern_str = '/'.join(step_pattern)
            # check whether we can make a next step
            next_step = self._registry.lookup(provided, IStep,
                                              step_pattern_str)
            
            if next_step is not None:
                # if so, that's the pattern we matched
                pattern = step_pattern
                pattern_str = step_pattern_str
            else:
                # if not, see whether we can match a variable
                variable_pattern = pattern + (':',)
                variable_pattern_str = '/'.join(variable_pattern)
                variable = self._registry.lookup(provided, IStep,
                                                 variable_pattern_str)
                if variable is not None:
                    # if so, we matched the variable pattern
                    pattern = variable_pattern
                    pattern_str = variable_pattern_str
                    # we parse the variable to see whether the name
                    # fits what we expect
                    if ':' in variable:
                        variable, converter_name = variable.split(':')
                    else:
                        converter_name = 'unicode'
                    converter = self._converters[converter_name]
                    try:
                        converted = converter(name)
                    except ValueError:
                        stack.append(name)
                        return stack, consumed, obj
                    # the variable name is registered
                    variables[str(variable)] = converted
                else:
                    # cannot find step or variable, so cannot resolve
                    stack.append(name)
                    return stack, consumed, obj
            # now see about constructing the object
            factory = self._registry.lookup(provided, IFactory, pattern_str)
            if factory is None:
                factory = default_factory
            parent = obj
            obj = factory(**variables)    
            if obj is None:
                stack.append(name)
                # we cannot resolve to a factory that returns None
                return stack, consumed, parent
            consumed.append(name)
            obj.__name__ = name
            obj.__parent__ = parent
        return stack, consumed, obj

    def locate(self, root, model, default):
        if hasattr(model, '__parent__') and model.__parent__ is not None:
            return
    
        root_interface = providedBy(root)
        model_interface = providedBy(model)
        v = self._inverse_registry.lookup(
            (root_interface, model_interface), IInverse, name=u'')
        if v is None:
            raise LocationError("Cannot reconstruct parameters of: %s" % model)
        pattern, inverse = v
        gen_pattern = generalize_pattern(pattern)

        # obtain the variables
        variables = inverse(model)
        variables = dict([(str(key), value) for (key, value) in
                          variables.items()])
        pattern = list(pattern)
        gen_pattern = list(gen_pattern)
        while True:
            name = pattern.pop()                
            gen_name = gen_pattern.pop()
    
            if gen_name == ':':
                name = name[1:]
                if ':' in name:
                    name, converter_name = name.split(':')
                name = variables.pop(name)  
            model.__name__ = unicode(name)
    
            # no more parents we can find, so we're at the root
            if not gen_pattern:
                model.__parent__ = root
                return
            factory = self._registry.lookup(
                (root_interface,), IFactory, name='/'.join(gen_pattern))
            
            if factory is None:
                factory = default
            parent = factory(**variables)
            model.__parent__ = parent
            model = parent
            
            if hasattr(model, '__parent__') and model.__parent__ is not None:
                # we're done, as parent as a parent itself
                return

def convert_unicodelist(s):
    return [convert_unicode(v) for v in s.split(';')]
    
def convert_strlist(s):
    return [convert_str(v) for v in s.split(';')]

def convert_intlist(s):
    return [int(v) for v in s.split(';')]

def convert_unicode(s):
    try:
        return unicode(s)
    except UnicodeError:
        raise ValueError

def convert_str(s):
    try:
        return str(s)
    except UnicodeError:
        raise ValueError

def normalize(pattern_str):
    if pattern_str.startswith('/'):
        return pattern_str[1:]
    return pattern_str

_patterns = Patterns()
register_converter = _patterns.register_converter
register = _patterns.register
register_inverse = _patterns.register_inverse
resolve = _patterns.resolve
resolve_stack = _patterns.resolve_stack
consume = _patterns.consume
consume_stack = _patterns.consume_stack
locate = _patterns.locate

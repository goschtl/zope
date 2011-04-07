##############################################################################
#
# Copyright (c) 2006-2008 Zope Foundation and Contributors.
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
import re
import os.path
import zc.buildout.buildout
import pprint
from zc.buildout.buildout import Options


def evaluate_macro(buildout, name, macro, input, recipe):
    def replace_match(match):
        key = match.groups()[0]
        if key in buildout[input]:
            ret_val = '${%s:%s}' % (input, key)
            if key in new_macro:
                new_macro[key] = ret_val
        else:
            ret_val = '${%s:%s}' % (name, key)
        return ret_val
    c_re = re.compile(r'\$\$\{:([^}]*)\}')
    new_macro = dict(macro)
    for key, value in dict(macro).iteritems():
        if new_macro.get(key, '') == value:
            new_macro[key] = c_re.sub(
                replace_match, value.replace('$${:__name__}', name))
    if recipe:
        new_macro['recipe'] = recipe
    return new_macro

def parse_target(invoker, target):
    input_section = invoker
    if ':' in target:
        target, input_section = target.split(':')
    return target, input_section

def get_recipe(invocation_section, macro_section, parameter_section, default=None):
    if 'recipe' in parameter_section:
        return parameter_section['recipe']
    elif 'result-recipe' in parameter_section:
        return parameter_section['result-recipe']
    elif 'result-recipe' in invocation_section:
        return invocation_section['result-recipe']
    elif 'recipe' in macro_section:
        return macro_section['recipe']
    else:
        return default


def Macro(buildout, name, options):
    del options['recipe']
    macro = options.pop('macro').strip()
    targets = options.pop('targets', name).strip().split()
    macro_summation = {}

    macro_summation.update(dict(buildout[macro]))

    new_sections = []
    for output, input in (parse_target(name, target) for target in targets):
        recipe = get_recipe(options, macro_summation, buildout[input])
        new_sections.append(output)
        opt = Options(
                buildout,
                output,
                evaluate_macro(
                    buildout, output, macro_summation, input, recipe))
        opt.pop('result-recipe', '')
        if output == name:
            # If we're targetting the invoker
            options._raw.update(opt._raw)
            options['recipe'] = options.get('recipe', 'zc.recipe.macro:empty')
        else:
            # If we're targetting some other section
            buildout._raw[output] = opt._raw
    options.pop('result-recipe', '')

    #Make a result-sections variable holding the sections that are modified
    if new_sections:
        options['result-sections'] = ' '.join(new_sections)

    #Make sure we have a recipe for this part, even if it is only the empty
    #one.
    if not options.get('recipe', None):
        options['recipe'] = 'zc.recipe.macro:empty'

    #Install the resulting recipe
    reqs, entry = zc.buildout.buildout._recipe(options._data)
    recipe_class = zc.buildout.buildout._install_and_load(
        reqs, 'zc.buildout', entry, buildout)

    __doing__ = 'Initializing part %s.', name
    part = recipe_class(buildout, name, options)
    return part


class Empty(object):
    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

    def install(self):
        return []

    update = install

    def uninstall(self):
        pass


class Test(object):

    def __init__(self, buildout, name, options):
        self.name = name
        self.buildout = buildout
        self.options = options

    def install(self):
        return []

    update = install

    def uninstall(self):
        pass



# -*- coding: utf-8 -*-

import martian


class use_hash(martian.Directive):
    scope = martian.CLASS_OR_MODULE
    store = martian.ONCE
    default = True

    def factory(self, value):
        return bool(value)


class inclusion(martian.Directive):
    scope = martian.CLASS
    store = martian.MULTIPLE

    def factory(self, name, file, depends=[], bottom=False):
        return (name, file, depends, bottom)


class include(martian.Directive):
    scope = martian.CLASS
    store = martian.MULTIPLE
    
    def factory(self, value, name=None, bottom=False):
        return (value, name, bottom)


class need(martian.Directive):
    scope = martian.CLASS
    store = martian.MULTIPLE

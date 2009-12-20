# -*- coding: utf-8 -*-

import martian


class use_hash(martian.Directive):
    scope = martian.CLASS_OR_MODULE
    store = martian.ONCE
    default = True

    def factory(self, value):
        return bool(value)


class include(martian.Directive):
    scope = martian.CLASS
    store = martian.MULTIPLE
    
    def factory(self, resource):
        return resource

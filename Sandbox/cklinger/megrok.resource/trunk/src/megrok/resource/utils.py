#!/usr/bin/python
# -*- coding: utf-8 -*-

from megrok.resource import include

def component_includes(component, *resources):
    include.set(component, resources)

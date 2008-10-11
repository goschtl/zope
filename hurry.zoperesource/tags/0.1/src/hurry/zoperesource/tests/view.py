from zope import component
from hurry.resource.interfaces import ICurrentNeededInclusions
from hurry.resource import Library, ResourceInclusion

foo = Library("foo")

a = ResourceInclusion(foo, "a.js")

b = ResourceInclusion(foo, "b.js", depends=[a])

class TestSingle(object):
    def widget(self):
        a.need()
        return "the widget HTML itself"

class TestMultiple(object):
    def widget(self):
        b.need()
        return "the widget HTML itself"

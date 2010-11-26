from fanstatic import Library, ResourceInclusion, get_current_needed_inclusions

foo = Library("foo", "foo_dir")

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

class TestBottom(object):
    def widget(self):
        b.need()
        # XXX this does not use any official API and needs to be
        # reconsidered. Its done anyway now to make the tests pass,
        # instead of just removing the corresponding test.
        get_current_needed_inclusions()._bottom = True
        get_current_needed_inclusions()._force_bottom = True
        return "the widget HTML itself"

class TestInlineResource(object):
    pass

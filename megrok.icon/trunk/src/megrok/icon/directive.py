import martian


class icon(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE

    def factory(self, name, registry='common'):
        return (name, registry)

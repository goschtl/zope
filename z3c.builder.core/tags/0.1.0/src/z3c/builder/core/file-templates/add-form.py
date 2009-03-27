class %(className)s(AddForm):
    """Add form for %(interface)s"""

    label = u'%(label)s'
    fields = Fields(%(interface)s).select(%(fields)s)

    def create(self, data):
        object = %(factory)s()
        for name, value in data.items():
            setattr(object, name, value)
        return object

    def add(self, object):
        count = 0
        while '%(factory)s-%%i' %%count in self.context:
            count += 1;
        self._name = '%(factory)s-%%i' %%count
        self.context[self._name] = object
        return object

    def nextURL(self):
        return absoluteURL(
            self.context[self._name], self.request) + '/%(next)s'

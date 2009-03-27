class %(className)s(DisplayForm, Form):
    """Display form for %(interface)s"""
    fields = Fields(%(interface)s).select(%(fields)s)

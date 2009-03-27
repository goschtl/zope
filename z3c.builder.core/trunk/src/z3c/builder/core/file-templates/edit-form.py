class %(className)s(EditForm):
    """Edit form for %(interface)s"""

    label = u'%(label)s'
    fields = Fields(%(interface)s).select(%(fields)s)

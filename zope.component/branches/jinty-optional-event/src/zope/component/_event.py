try:
    # use zope.event if it's around
    from zope.event import subscribers, notify
except ImportError:
    # if not, provide our own implementation
    subscribers = []

    def notify(event):
        for subscriber in subscribers:
            subscriber(event)

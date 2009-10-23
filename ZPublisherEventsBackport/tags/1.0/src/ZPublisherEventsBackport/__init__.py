try:
    import ZPublisher.interfaces
except ImportError:
    import logging
    import sys
    import ZPublisher
    import ZPublisher.Publish
    from ZPublisherEventsBackport import interfaces
    sys.modules['ZPublisher.interfaces'] = interfaces
    ZPublisher.interfaces = interfaces
    for name, iface in interfaces.__dict__.items():
        if name.startswith('IPub'):
            iface.__module__ = 'ZPublisher.interfaces'
            iface.__identifier__ = "%s.%s" % (iface.__module__, iface.__name__)
            iface.changed(None)
    
    from ZPublisherEventsBackport import patch
    ZPublisher.Publish.publish=patch.publish
    logging.info("Monkeypatch ZPublisher publish with publication events")

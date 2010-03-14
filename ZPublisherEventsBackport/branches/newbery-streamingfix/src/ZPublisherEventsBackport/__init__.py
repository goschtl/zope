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

    # the monkey patch for `ZPublisher.Publish.get_module_info` from
    # `plone.app.linkintegrity` needs to be applied first in order for
    # our patch to find the right exception hook, which in turn keeps
    # plone's linkintegrity feature working...
    try:
        from plone.app.linkintegrity import monkey
        monkey.installExceptionHook()
    except ImportError:
        pass

    from ZPublisherEventsBackport import patch
    ZPublisher.Publish.publish=patch.publish
    logging.info("Monkeypatch ZPublisher publish with publication events")

try:
    import ZPublisher.interfaces
    from ZPublisherEventsBackport import patch_212 as patch
except ImportError:
    import logging
    import sys
    import ZPublisher
    from ZPublisherEventsBackport import interfaces
    sys.modules['ZPublisher.interfaces'] = interfaces
    ZPublisher.interfaces = interfaces
    for name, iface in interfaces.__dict__.items():
        if name.startswith('IPub'):
            iface.__module__ = 'ZPublisher.interfaces'
            iface.__identifier__ = "%s.%s" % (iface.__module__, iface.__name__)
            iface.changed(None)
    from ZPublisherEventsBackport import patch

# Applying the following patches to both the old and new Zope releases
# until we can get the updated PubSuccess events in the next release	

# the monkey patch for `ZPublisher.Publish.get_module_info` from
# `plone.app.linkintegrity` needs to be applied first in order for
# our patch to find the right exception hook, which in turn keeps
# plone's linkintegrity feature working...
try:
    from plone.app.linkintegrity import monkey
    monkey.installExceptionHook()
except ImportError:
    pass

from patch_write import zserver_write, zpublisher_write
from patch_ofs_image import index_html, _range_request_handler

# an updated version of the old patch
import ZPublisher.Publish
ZPublisher.Publish.publish = patch.publish
logging.info("Monkeypatch ZPublisher publish with publication events")

# passing the request to 'write' for the PubSuccess event
import OFS.Image.File
OFS.Image.File.index_html = patch_ofs_image.index_html
OFS.Image.File._range_request_handler = patch_ofs_image._range_request_handler
logging.info("Monkeypatch OFS.Image.File to support PubSuccess event")

# adding the PubSuccess event to 'write'
import ZServer.HTTPResponse
ZServer.HTTPResponse.ZServerHTTPResponse.write = patch_write.zserver_write
logging.info("Monkeypatch ZServer.HTTPResponse.write with PubSuccess event")

# adding the PubSuccess event to 'write'
# not sure if this last one is necessary but it doesn't hurt
import ZPublisher.HTTPResponse
ZPublisher.HTTPResponse.HTTPResponse.write = patch_write.zpublisher_write
logging.info("Monkeypatch ZPublisher.HTTPResponse.write with PubSuccess event")


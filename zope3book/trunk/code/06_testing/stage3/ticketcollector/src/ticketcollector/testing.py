import os
from zope.app.testing.functional import ZCMLLayer

TicketCollectorLayer = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'TicketCollectorLayer', allow_teardown=True)

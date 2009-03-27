"""Error Reporting.

$Id$
"""
import transaction

from zope.app.appsetup.bootstrap import ensureUtility, getInformationFromEvent

from zope.error.error import RootErrorReportingUtility
from zope.error.interfaces import IErrorReportingUtility

def errorSubscriber(event):
    """Subscriber to the IDataBaseOpenedEvent

    Create utility at that time if not yet present
    """

    db, connection, root, root_folder = getInformationFromEvent(event)

    ensureUtility(root_folder, IErrorReportingUtility, '',
                  RootErrorReportingUtility, copy_to_zlog=True,
                  _ignored_exceptions=('Unauthorized',), asObject=True)

    transaction.commit()
    connection.close()

globalErrorReportingUtility = RootErrorReportingUtility()
globalErrorReportingUtility.setProperties(20, True, ())

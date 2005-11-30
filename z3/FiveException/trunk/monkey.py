import sys
from types import StringType, ListType

import AccessControl.User
from Acquisition import aq_acquire
from ZODB.POSException import ConflictError
from zLOG import LOG, INFO, BLATHER
import ZPublisher
from Zope.App.startup import RequestContainer, app
from zope.component import getView, ComponentLookupError

from Products.FiveException.interfaces import IZope2HandledException

def zpublisher_exception_hook(published, REQUEST, t, v, traceback):
    try:
        if isinstance(t, StringType):
            if t.lower() in ('unauthorized', 'redirect'):
                raise
        else:
            if t is SystemExit:
                raise
            if issubclass(t, ConflictError):
                # First, we need to close the current connection. We'll
                # do this by releasing the hold on it. There should be
                # some sane protocol for this, but for now we'll use
                # brute force:
                global conflict_errors
                conflict_errors = conflict_errors + 1
                method_name = REQUEST.get('PATH_INFO', '')
                err = ('ZODB conflict error at %s '
                       '(%s conflicts since startup at %s)')
                LOG(err % (method_name, conflict_errors, startup_time),
                    INFO, '')
                LOG('Conflict traceback', BLATHER, '', error=sys.exc_info())
                raise ZPublisher.Retry(t, v, traceback)
            if t is ZPublisher.Retry: v.reraise()

        try:
            log = aq_acquire(published, '__error_log__', containment=1)
        except AttributeError:
            error_log_url = ''
        else:
            error_log_url = log.raising((t, v, traceback))

        if (getattr(REQUEST.get('RESPONSE', None), '_error_format', '')
            !='text/html'):
            raise t, v, traceback

        # XXX do we need this? published is not used by us anymore
        if (published is None or published is app or
            type(published) is ListType):
            # At least get the top-level object
            published=app.__bobo_traverse__(REQUEST).__of__(
                RequestContainer(REQUEST))

        # XXX do we need this?
        if REQUEST.get('AUTHENTICATED_USER', None) is None:
            REQUEST['AUTHENTICATED_USER']=AccessControl.User.nobody

        # XXX look for zope 3 views instead from here
        # and then raise the rendered string like raise_standardErrorMessage
        # does
        
        # if it's a zope 2 handled exception, we want to bail out to
        # zope 2 handling immediately
        if IZope2HandledException.providedBy(v):
            raise t, v, traceback
        
        try:
            view = getView(v, 'index.html', REQUEST)
        except ComponentLookupError:
            raise t, v, traceback
        # XXX utter hack here to fool Five into working. Five should
        # be using aq_inner() and then this hack can be removed.
        v.aq_inner = v
        view = view.__of__(published)
        message = view()
        raise t, message, traceback
    finally:
        traceback=None


def installExceptionHook():
    print "loading our special error hook!"

    # XXX really hairy hack to get the modules dictionary from the
    # default argument of get_module_info. We need to modify this in order
    # modify the err_hook (which is zpublisher_exception_hook) after Zope
    # has already started up
    from ZPublisher.Publish import get_module_info
    # we need to call this once to initialize the modules dictionary
    get_module_info('Zope')
    modules = get_module_info.func_defaults[0]

    (bobo_before, bobo_after, object, realm, debug_mode, err_hook,
     validated_hook, transactions_manager)= modules['Zope']
    modules['Zope'] = (bobo_before, bobo_after, object, realm,
                       debug_mode, zpublisher_exception_hook,
                       validated_hook, transactions_manager)


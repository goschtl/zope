import logging
import sys
from ZPublisher.Publish import call_object
from ZPublisher.Publish import missing_name
from ZPublisher.Publish import dont_publish_class
from ZPublisher.Publish import get_module_info
from ZPublisher.Publish import Retry
from ZPublisher.mapply import mapply
from zope.publisher.browser import setDefaultSkin
from zope.security.management import newInteraction
from zope.security.management import endInteraction
from zExceptions import Redirect

import zope.event
from plone.postpublicationhook.event import AfterPublicationEvent


def publish(request, module_name, after_list, debug=0,
            # Optimize:
            call_object=call_object,
            missing_name=missing_name,
            dont_publish_class=dont_publish_class,
            mapply=mapply,
            ):

    (bobo_before, bobo_after, object, realm, debug_mode, err_hook,
     validated_hook, transactions_manager)= get_module_info(module_name)

    parents=None
    response=None

    try:
        # TODO pass request here once BaseRequest implements IParticipation
        newInteraction()

        request.processInputs()

        request_get=request.get
        response=request.response

        # First check for "cancel" redirect:
        if request_get('SUBMIT','').strip().lower()=='cancel':
            cancel=request_get('CANCEL_ACTION','')
            if cancel:
                raise Redirect, cancel

        after_list[0]=bobo_after
        if debug_mode:
            response.debug_mode=debug_mode
        if realm and not request.get('REMOTE_USER',None):
            response.realm=realm

        if bobo_before is not None:
            bobo_before()

        # Get the path list.
        # According to RFC1738 a trailing space in the path is valid.
        path=request_get('PATH_INFO')

        request['PARENTS']=parents=[object]

        if transactions_manager:
            transactions_manager.begin()

        object=request.traverse(path, validated_hook=validated_hook)

        if transactions_manager:
            transactions_manager.recordMetaData(object, request)

        result=mapply(object, request.args, request,
                      call_object,1,
                      missing_name,
                      dont_publish_class,
                      request, bind=1)

        if result is not response:
            response.setBody(result)

        # This is the only change from the canonical publish method
        zope.event.notify(AfterPublicationEvent(object, request))

        if transactions_manager:
            transactions_manager.commit()
        endInteraction()

        return response
    except:
        # DM: provide nicer error message for FTP
        sm = None
        if response is not None:
            sm = getattr(response, "setMessage", None)

        if sm is not None:
            from asyncore import compact_traceback
            cl,val= sys.exc_info()[:2]
            sm('%s: %s %s' % (
                getattr(cl,'__name__',cl), val,
                debug_mode and compact_traceback()[-1] or ''))

        if err_hook is not None:
            if parents:
                parents=parents[0]
            try:
                try:
                    return err_hook(parents, request,
                                    sys.exc_info()[0],
                                    sys.exc_info()[1],
                                    sys.exc_info()[2],
                                    )
                except Retry:
                    if not request.supports_retry():
                        return err_hook(parents, request,
                                        sys.exc_info()[0],
                                        sys.exc_info()[1],
                                        sys.exc_info()[2],
                                        )
            finally:
                if transactions_manager:
                    transactions_manager.abort()
                endInteraction()

            # Only reachable if Retry is raised and request supports retry.
            newrequest=request.retry()
            request.close()  # Free resources held by the request.
            # Set the default layer/skin on the newly generated request
            setDefaultSkin(newrequest)
            try:
                return publish(newrequest, module_name, after_list, debug)
            finally:
                newrequest.close()

        else:
            if transactions_manager:
                transactions_manager.abort()
            endInteraction()
            raise



def InstallHook():
    """Install our own publish method."""
    from plone.postpublicationhook import hook
    import ZPublisher.Publish

    ZPublisher.Publish.publish=hook.publish
    logging.info("Monkeypatch ZPublisher publish method to send AfterPublicationEvent")


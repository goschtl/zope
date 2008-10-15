import logging
from zope.event import notify
from plone.validatehook.event import PostValidationEvent

logger = logging.getLogger("plone.validatehook")


class ValidateHookWrapper:
    """Utility method to facilitate wrapping of the zpublisher validation
    hook. This hook is called after traversal has finished and after a
    user has been validated."""

    def __init__(self, module):
        self.original_hook=getattr(module, 'zpublisher_validated_hook', None)

    def __call__(self, request, user):
        if self.original_hook is not None:
            self.original_hook(request, user)

        context=request.PARENTS[0]
        notify(PostValidationEvent(context, request, user))


def InstallHook():
    """Installs our own validation hook.

    Note that we can not change Zope2.zpublisher_validated_hook since
    the Zope startup code sets that *after* product initialization.
    """
    from Zope2.App import startup
    startup.validated_hook=ValidateHookWrapper(startup.validated_hook)

    logger.info("Wrapped the Zope2 zpublisher validation hook")


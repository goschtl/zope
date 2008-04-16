try:
    from zope.component import eventtesting
except ImportError:
    from zope.app.event.tests import placelesssetup as eventtesting

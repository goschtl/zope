try:
    from zope.component import eventtesting
    eventtesting  # pyflakes
except ImportError:
    from zope.app.event.tests import placelesssetup as eventtesting
    eventtesting  # pyflakes

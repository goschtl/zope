from z3c.form.form import EditForm
from z3c.form.field import Fields

from z3c.feature.core.unittest import TestingFeature
from z3c.feature.core import interfaces


class TestingWebView(EditForm):
    fields = Fields(interfaces.ITestingFeature)


class TestingWebFeature(object):
    viewFactory = TestingWebView
    contentFactory = TestingFeature
    title = u"Automated Tests"
    description = (u"Adds all the boiler plate for running an "
                   u"automated doctest suite along with test "
                   u"coverage reporting.")

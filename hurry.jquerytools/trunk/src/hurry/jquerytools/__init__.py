from hurry.resource import Library, ResourceInclusion, GroupInclusion
from hurry.jquery import jquery

JqueryToolsLibrary = Library('jquery-build')

jquerytools = ResourceInclusion(
    JqueryToolsLibrary, 'jquery.tools.min.js', depends=[jquery])


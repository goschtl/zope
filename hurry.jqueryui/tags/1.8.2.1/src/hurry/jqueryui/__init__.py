from hurry.resource import Library, ResourceInclusion
from hurry.jquery import jquery
try:
    from hurry.jqueryui._themes import *
except ImportError:
    pass

jqueryui = Library('jqueryui')

jqueryui = ResourceInclusion(jqueryui, 'jquery-ui.js', depends=[jquery],
                             minified='jquery-ui.min.js')


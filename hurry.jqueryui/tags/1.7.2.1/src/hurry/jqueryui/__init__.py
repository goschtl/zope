from hurry.resource import Library, ResourceInclusion
from hurry.jquery import jquery
from hurry.jqueryui._themes import *

jqueryui = Library('jqueryui')

jqueryui = ResourceInclusion(jqueryui, 'jquery-ui.js', depends=[jquery],
                             minified='jquery-ui.min.js')


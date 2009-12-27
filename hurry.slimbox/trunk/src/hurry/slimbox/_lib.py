from hurry.resource import Library, ResourceInclusion, GroupInclusion
from hurry.jquery import jquery

SlimboxLibrary = Library('SlimboxLibrary')

slimbox_css = ResourceInclusion(
    SlimboxLibrary, 'slimbox-2.03/css/slimbox2.css')

slimbox_js = ResourceInclusion(
    SlimboxLibrary, 'slimbox-2.03/js/slimbox2.js', depends=[jquery])

slimbox = GroupInclusion([slimbox_css, slimbox_js])

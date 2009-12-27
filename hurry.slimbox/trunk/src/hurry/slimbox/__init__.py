from hurry.resource import Library, ResourceInclusion, GroupInclusion
from hurry.jquery import jquery

SlimboxLibrary = Library('SlimboxLibrary')

slimbox_css = ResourceInclusion(
    SlimboxLibrary, 'css/slimbox2.css')

slimbox_js = ResourceInclusion(
    SlimboxLibrary, 'js/slimbox2.js', depends=[jquery])

slimbox = GroupInclusion([slimbox_css, slimbox_js])

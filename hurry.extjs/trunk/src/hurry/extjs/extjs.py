from hurry.resource import Library, ResourceInclusion

extjs = Library('extjs')

extjs_core = ResourceInclusion(extjs, 'ext-core.js',
                               debug='ext-core-debug.js')

extjs_all = ResourceInclusion(extjs, 'ext-all.js', depends=[extjs_core],
                              debug='ext-all-debug.js')

extjs_css = ResourceInclusion(extjs, 'resources/css/ext-all.css')

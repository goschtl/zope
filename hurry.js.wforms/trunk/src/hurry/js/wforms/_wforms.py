from hurry.resource import Library, ResourceInclusion

wforms_lib = Library('wforms')

# includes the base2 library (1.0b2)
wforms = ResourceInclusion(wforms_lib,
                           'wforms.js',
                           minified='wforms_pack.js')

# not very useful right now, but in the future we might pack the base2
# library and make this depend on it
wforms_alone = ResourceInclusion(wforms_lib,
                                 'wforms_alone.js',
                                 minified='wforms_alone_pack.js')

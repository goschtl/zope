from hurry.resource import Library, ResourceInclusion

base2_lib = Library('base2')

dom = ResourceInclusion(base2_lib,
                        'src/base2-dom-strict.js',
                        minified='base2-dom-p.js')

                        
tinymce = ResourceInclusion(tinymce_lib, 'tiny_mce_src.js',
                            minified='tiny_mce.js')


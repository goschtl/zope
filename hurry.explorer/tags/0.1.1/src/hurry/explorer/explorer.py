from hurry.resource import Library, ResourceInclusion
from hurry import yui

explorer_lib = Library('explorer')

explorer = ResourceInclusion(explorer_lib, 'explorer.js',
                             depends=[yui.connection, yui.tabview,
                                      yui.json, yui.treeview, yui.history,
                                      yui.datasource, yui.datatable,
                                      yui.button],
                             bottom=True,
                             )


# -*- coding: utf-8 -*-

import martian
import grokcore.view
import megrok.z3ctable
import grokcore.component

from zope import component
from z3c.table.interfaces import ITable
from grokcore.component.scan import determine_module_component
from grokcore.component.meta import default_provides as default
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class TableGrokker(martian.GlobalGrokker):
    """Grokker dedicated to find the table within a module.
    This allows to set implicit relationships bewteen a table and a column.
    """
    martian.priority(991)

    def grok(self, name, module, module_info, config, **kw):
        table = determine_module_component(module_info,
                                           megrok.z3ctable.table,
                                           megrok.z3ctable.ITable)
        megrok.z3ctable.table.set(module, table)
        return True


class ColumnGrokker(martian.ClassGrokker):
    martian.priority(990)
    martian.component(megrok.z3ctable.components.Column)

    martian.directive(grokcore.component.name)
    martian.directive(grokcore.component.context)
    martian.directive(megrok.z3ctable.table, default=ITable)
    martian.directive(grokcore.component.provides, get_default=default)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)

    def execute(self, factory, config, layer, context, table, provides, name):
        for_ = (context, layer, table)
        config.action(
            discriminator=('adapter', for_, provides, name),
            callable=component.provideAdapter,
            args=(factory, for_, provides, name),
            )
        return True

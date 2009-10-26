import grokcore.component as grok
import grokcore.view as view
import megrok.layout
import z3c.tabular.table

from grokcore.view.interfaces import ITemplate as IGrokTemplate
from z3c.template.template import getPageTemplate


class BaseTable(view.View):
    grok.baseclass()
    status = None # The Tabular stuff checks if the status is None
    template = None

    def render(self):
        template = getPageTemplate()
        return template(self)

    render.base_method = True
    renderFormTable = render


class FormTable(BaseTable, z3c.tabular.table.FormTable):
    """ A Form Table Class. You have to define your buttons and stuff yourself
    """

    def update(self):
        view.View.update(self)
        z3c.tabular.table.FormTable.update(self)


class DeleteFormTable(BaseTable, z3c.tabular.table.DeleteFormTable):
    """ This is a table with has logic for deleteing stuff on it
    """

    def update(self):
        view.View.update(self)
        z3c.tabular.table.DeleteFormTable.update(self)


class FormTablePage(megrok.layout.Page, z3c.tabular.table.FormTable):
    """ A Form Table Class which get renderd inside a Layout
    """
    grok.baseclass()
    template = None

    def update(self):
        megrok.layout.Page.update(self)
        z3c.tabular.table.FormTable.update(self)

    def render(self):
        template = getPageTemplate()
        return template(self)

    render.base_method = True
    renderFormTable = render


class DeleteFormTablePage(megrok.layout.Page,
                          z3c.tabular.table.DeleteFormTable):
    """ A Form Table with has support for removing objects form a folder
    """
    grok.baseclass()

    template = None

    def update(self):
        megrok.layout.Page.update(self)
        z3c.tabular.table.DeleteFormTable.update(self)

    def render(self):
        template = getPageTemplate()
        return template(self)

    render.base_method = True
    renderFormTable = render

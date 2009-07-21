import os
import warnings
import zope.component
import grokcore.component
import grokcore.view
from martian.error import GrokError
from grokcore.view.interfaces import ITemplateFileFactory, TemplateLookupError
from grokcore.view.components import PageTemplate


class InlineTemplateRegistry(object):
    def __init__(self):
        self._reg = {}
        self._unassociated = set()


    def register_inline_template(self, module_info, template_name, template):
        # verify no file template got registered with the same name
        try:
            existing_template = file_template_registry.lookup(
                module_info, template_name)
        except TemplateLookupError:
            pass
        else:
            template_dir = file_template_registry.get_template_dir(module_info)
            raise GrokError("Conflicting templates found for name '%s': "
                            "the inline template in module '%s' conflicts "
                            "with the file template in directory '%s'" %
                            (template_name, module_info.dotted_name,
                             template_dir), None)

        # register the inline template
        self._reg[(module_info.dotted_name, template_name)] = template
        self._unassociated.add((module_info.dotted_name, template_name))

    def associate(self, module_info, template_name):
        self._unassociated.remove((module_info.dotted_name, template_name))

    def lookup(self, module_info, template_name):
        result = self._reg.get((module_info.dotted_name, template_name))
        if result is None:
            raise TemplateLookupError("inline template '%s' in '%s' cannot be found" % (
                    template_name, module_info.dotted_name))
        return result
    
    def unassociated(self):
        return self._unassociated

class FileTemplateRegistry(object):
    def __init__(self):
        self._reg = {}
        self._unassociated = set()

    def register_directory(self, module_info):
        # we cannot register a templates dir for a package
        if module_info.isPackage():
            return

        template_dir = self.get_template_dir(module_info)
        # we can only register for directories
        if not os.path.isdir(template_dir):
            return
    
        for template_file in os.listdir(template_dir):
            template_path = os.path.join(template_dir, template_file)
            self._register_template_file(module_info, template_path)
        
    def _register_template_file(self, module_info, template_path):
        template_dir, template_file = os.path.split(template_path)

        if template_file.startswith('.') or template_file.endswith('~'):
            return
        if template_file.endswith('.cache'):
            # chameleon creates '<tpl_name>.cache' files on the fly
            return

        template_name, extension = os.path.splitext(template_file)
        if (template_dir, template_name) in self._reg:
            raise GrokError("Conflicting templates found for name '%s' "
                            "in directory '%s': multiple templates with "
                            "the same name and different extensions ." %
                            (template_name, template_dir), None)
        # verify no inline template exists with the same name
        try:
            inline_template_registry.lookup(module_info, template_name)
        except TemplateLookupError:
            pass
        else:
            raise GrokError("Conflicting templates found for name '%s': "
                            "the inline template in module '%s' conflicts "
                            "with the file template in directory '%s'" %
                            (template_name, module_info.dotted_name,
                             template_dir), None)
        
        extension = extension[1:] # Get rid of the leading dot.
        template_factory = zope.component.queryUtility(
            grokcore.view.interfaces.ITemplateFileFactory,
            name=extension)

        if template_factory is None:
            # Warning when importing files. This should be
            # allowed because people may be using editors that generate
            # '.bak' files and such.
            warnings.warn("File '%s' has an unrecognized extension in "
                          "directory '%s'" %
                          (template_file, template_dir), UserWarning, 2)
            return
        template = template_factory(template_file, template_dir)
        # XXX this isn't defined in the interface or anywhere...
        template._annotateGrokInfo(template_name, template_path)

        self._reg[(template_dir, template_name)] = template
        self._unassociated.add(template_path)
        
    def associate(self, template_path):
        self._unassociated.remove(template_path)

    def lookup(self, module_info, template_name):
        template_dir = self.get_template_dir(module_info)
        result = self._reg.get((template_dir, template_name))
        if result is None:
            raise TemplateLookupError("template '%s' in '%s' cannot be found" % (
                    template_name, template_dir))
        return result
    
    def unassociated(self):
        return self._unassociated
        
    def get_template_dir(self, module_info):
        template_dir_name = grokcore.view.templatedir.bind().get(
            module=module_info.getModule())
        if template_dir_name is None:
            template_dir_name = module_info.name + '_templates'

        template_dir = module_info.getResourcePath(template_dir_name)
        return template_dir

inline_template_registry = InlineTemplateRegistry()
file_template_registry = FileTemplateRegistry()

register_inline_template = inline_template_registry.register_inline_template

register_directory = file_template_registry.register_directory
    
all_directory_templates_registries = {}

def lookup(module_info, template_name):
    try:
        return file_template_registry.lookup(module_info, template_name)
    except TemplateLookupError, e:
        try:
            return inline_template_registry.lookup(module_info, template_name)
        except TemplateLookupError, e2:
            # re-raise first error again
            raise e

class BaseTemplateRegistry(object):

    def __init__(self):
        self._reg = {}

    def register(self, name, template):
        self._reg[name] = dict(template=template, associated=False)

    def markAssociated(self, name):
        entry = self._getEntry(name)
        entry['associated'] = True

    def _getEntry(self, name):
        return self._reg.get(name)

    def get(self, name):
        entry = self._getEntry(name)
        if entry is None:
            return None
        return entry['template']

    def listUnassociated(self):
        for name, entry in self._reg.iteritems():
            if not entry['associated']:
                yield name


class ModuleTemplateRegistry(BaseTemplateRegistry):

    _directory_registry = None

    def initializeDirectoryRegistry(self, template_dir):
        if template_dir is not None:
            if not template_dir in all_directory_templates_registries:
                all_directory_templates_registries[template_dir] = DirectoryTemplateRegistry(template_dir)
            self._directory_registry = all_directory_templates_registries[template_dir]

    def _getEntry(self, name):
        entry = super(ModuleTemplateRegistry, self)._getEntry(name)
        # self._directory_registry has not been instanciated when registering instance templates
        if entry is None and self._directory_registry is not None:
            entry = self._directory_registry._getEntry(name)
        return entry

    def getLocal(self, name):
        entry = self._reg.get(name)
        if entry is None:
            return None
        return entry['template']

    def _getTemplateDir(self, module_info):
        template_dir_name = grokcore.view.templatedir.bind().get(
            module=module_info.getModule())
        if template_dir_name is None:
            template_dir_name = module_info.name + '_templates'

        template_dir = module_info.getResourcePath(template_dir_name)

        return template_dir

    def findFilesystem(self, module_info):
        template_dir = self._getTemplateDir(module_info)

        if not os.path.isdir(template_dir):
            return

        self.initializeDirectoryRegistry(template_dir)

        if module_info.isPackage():
            return

        for template_file in os.listdir(template_dir):
            if template_file.startswith('.') or template_file.endswith('~'):
                continue
            if template_file.endswith('.cache'):
                # chameleon creates '<tpl_name>.cache' files on the fly
                continue

            template_name, extension = os.path.splitext(template_file)
            extension = extension[1:] # Get rid of the leading dot.
            template_factory = zope.component.queryUtility(
                grokcore.view.interfaces.ITemplateFileFactory,
                name=extension)

            if template_factory is None:
                # Warning when importing files. This should be
                # allowed because people may be using editors that generate
                # '.bak' files and such.
                warnings.warn("File '%s' has an unrecognized extension in "
                              "directory '%s'" %
                              (template_file, template_dir), UserWarning, 2)
                continue

            inline_template = self.getLocal(template_name)
            if inline_template:
                raise GrokError("Conflicting templates found for name '%s' "
                                "in module %r, either inline and in template "
                                "directory '%s', or two templates with the "
                                "same name and different extensions."
                                % (template_name, module_info.getModule(),
                                   template_dir), inline_template)

            if self._directory_registry._getEntry(template_name) is None:
                template = template_factory(template_file, template_dir)
                template_path = os.path.join(template_dir, template_file)
                template._annotateGrokInfo(template_name, template_path)

                self._directory_registry.register(template_name, template)

    def checkUnassociated(self, module_info):
        unassociated = list(self.listUnassociated())
        if unassociated:
            msg = (
                "Found the following unassociated template(s) when "
                "grokking %r: %s.  Define view classes inheriting "
                "from grok.View to enable the template(s)." % (
                module_info.dotted_name, ', '.join(unassociated)))
            warnings.warn(msg, UserWarning, 1)

        if self._directory_registry is not None:
            self._directory_registry.checkUnassociated(module_info)

    def checkTemplates(self, module_info, factory, component_name,
                       has_render, has_no_render):
        factory_name = factory.__name__.lower()
        template_name = grokcore.view.template.bind().get(factory)
        if template_name is None:
            template_name = factory_name

        if factory_name != template_name:
            # grok.template is being used

            if self.get(factory_name):
                raise GrokError("Multiple possible templates for %s %r. It "
                                "uses grok.template('%s'), but there is also "
                                "a template called '%s'."
                                % (component_name, factory, template_name,
                                   factory_name), factory)
        template = self.get(template_name)
        if template is not None:
            if has_render(factory):
                # we do not accept render and template both for a view
                # (unless it's a form, they happen to have render.
                raise GrokError(
                    "Multiple possible ways to render %s %r. "
                    "It has both a 'render' method as well as "
                    "an associated template." %
                    (component_name, factory), factory)
            self.markAssociated(template_name)
            factory.template = template
            template._initFactory(factory)
        else:
            if has_no_render(factory):
                # we do not accept a view without any way to render it
                raise GrokError("%s %r has no associated template or "
                                "'render' method." %
                                (component_name.title(), factory), factory)


class DirectoryTemplateRegistry(BaseTemplateRegistry):

    _checked = False

    def __init__(self, template_dir):
        super(DirectoryTemplateRegistry, self).__init__()
        self.template_dir = template_dir

    def checkUnassociated(self, module_info):
        if not self._checked:
            self._checked = True
            unassociated = list(self.listUnassociated())
            if unassociated:
                msg = (
                    "Found the following unassociated template(s) when "
                    "grokking directory %r: %s.  Define view classes inheriting "
                    "from grok.View to enable the template(s)." % (
                    self.template_dir, ', '.join(unassociated)))
                warnings.warn(msg, UserWarning, 1)


class PageTemplateFileFactory(grokcore.component.GlobalUtility):
    grokcore.component.implements(ITemplateFileFactory)
    grokcore.component.name('pt')

    def __call__(self, filename, _prefix=None):
        return PageTemplate(filename=filename, _prefix=_prefix)

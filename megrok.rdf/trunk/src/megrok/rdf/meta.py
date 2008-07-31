import martian
from martian.error import GrokError

from megrok import rdf

class ModelGrokker(martian.ClassGrokker):
    martian.component(rdf.Model)
    martian.directive(rdf.type)
    
    def execute(self, class_, config, type):
        rdf.rdftype_registry[unicode(type)] = class_
        return True

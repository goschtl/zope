# -*- coding: UTF-8 -*-

#plugins for object inspection
#object type determination may not be 100%

import sys
import copy
from z3c.zodbbrowser.bases import dataCollector, BaseObjectPlugin
from z3c.zodbbrowser.utils import *

from ZODB.utils import oid_repr, serial_repr
#force these attributes to be displayed
forceAttr = [('_p_oid', oid_repr),('_p_serial',serial_repr)]

class AnyObjectTypePlugin(BaseObjectPlugin):
    u"""Plugin for any object type
    this is the least specific plugin
    also implements some base methods for more specific plugins
    """
    def match(self, title):
        return True
    
    def getChildren(self):
        return dataCollector()
    
    def getProps(self):
        retval = dataCollector()
        
        try:
            itemz = copy.copy(self.context.__dict__)
            
            for attr, formatter in forceAttr:
                try:
                    kdata = getattr(self.context, attr)
                    
                    if formatter:
                        kdata=formatter(kdata)
                        
                    itemz[attr]=kdata
                except:
                    pass
            
            try:
                keyz=itemz.keys()
                keyz.sort()
                for key in keyz:
                    #if key.startswith('_'):
                    #    continue
                    #if key.startswith('__'):
                    #    continue
                    if key=='__parent__':
                        continue
                    kdata=itemz[key]
                    
                    retval.add(text = key, property=kdata)
            except:
                raise
        except AttributeError:
            pass
        
        return retval
    
    def getExpandable(self):
        return False
    
    def getType(self):
        try:
            return self.context.__class__.__name__
        except:
            return str(type(self.context))

class dictPlugin(AnyObjectTypePlugin):
    u"""Plugin for dict or dict-alike object type
    """
    def match(self, title):
        return isdict(self.context)
    
    def getChildren(self):
        retval = dataCollector()
        
        keyz = self.context.keys()
        try:
            keyz.sort()
        except:
            try:
                keyz=list(keyz)
                keyz.sort()
            except:
                pass
        
        for key in keyz:
            retval.add(text=safe_str(key), property=self.context[key])
        
        return retval
    
    def getExpandable(self):
        return True
    
    def getType(self):
        return 'dict'

class listPlugin(AnyObjectTypePlugin):
    u"""Plugin for list or list-alike object type
    """
    def match(self, title):
        return islist(self.context)
    
    def getChildren(self):
        retval = dataCollector()
        
        for d in self.context:
            retval.add(text = safe_str(d), property=d)
        
        return retval
    
    def getExpandable(self):
        return True
    
    def getType(self):
        return 'list'

class objectPlugin(AnyObjectTypePlugin):
    u"""Plugin for `user-defined` object types
    """
    def match(self, title):
        typ = str(type(self.context))
        return '.' in typ
    
    def getExpandable(self):
        return True
    
    def getType(self):
        return 'obj'


def main(PluginRegistry):
    PluginRegistry['object'].extend([
        (100,dictPlugin),
        (200,listPlugin),
        (sys.maxint-1, objectPlugin),
        (sys.maxint, AnyObjectTypePlugin)])
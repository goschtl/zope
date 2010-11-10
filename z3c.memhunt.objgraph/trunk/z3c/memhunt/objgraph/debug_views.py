import sys
import gc
import types
from tempfile import NamedTemporaryFile

try:
    from Products.Five.browser import BrowserView
    from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
except ImportError:
    from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile    
    from zope.publisher.browser import BrowserView

import checks
import pprint 
import guppy

heapy = guppy.hpy()


class DebugView(BrowserView):
    __allow_access_to_unprotected_subobjects__ = 1

    ref_template = ViewPageTemplateFile("zpt/ref_count.pt")
    ref_common_template = ViewPageTemplateFile("zpt/ref_common_count.pt")
    start_template = ViewPageTemplateFile("zpt/start.pt")

    evenOddClasses = ('even','odd')
    evenodd = 0

    def start(self):
        return self.start_template(self)

    def cssclass(self):
        """ determiner what background color to use for lists """
        if self.evenodd != 1:
            self.evenodd = 1
        else:
            self.evenodd = 0
        return self.evenOddClasses[self.evenodd]

    def ref_count(self):
        d = {}
        # collect all classes
        self.garbage_containing = len(gc.garbage)
        self.garbage_watching = len(gc.get_objects())
        self.total_ref_count = 0

        for m in sys.modules.values():
            for sym in dir(m):
                o = getattr (m, sym)
                if type(o) is types.ClassType:
                    d[o] = sys.getrefcount (o)

                    # sort by refcount
                    pairs = map (lambda x: (repr(x[0]),x[1]), d.items())
                    pairs.sort()
                    pairs.reverse()

        self.pairs = []
        for pair in pairs:
            self.total_ref_count += pair[1]
            self.pairs.append({'refcount':pair[1],
                               'name':pair[0]})

        self.pairs = sorted(self.pairs, key=lambda x: x['refcount'])
        self.pairs.reverse()


        return self.ref_template(self)

    def most_common(self):
        pairs = checks.most_common_types()
        self.pairs = []
        for pair in pairs:
            self.pairs.append({'refcount':pair[1],
                               'name':pair[0]})

        return self.ref_common_template(self)

    def display_mem(self):
        import malloc_stats
        return malloc_stats.malloc_stats()


    @property
    def target(self):
        if getattr(self, '_target', None):
            return getattr(self,'_target')

        target =  self.request.form.get('name','')
        if not target:
            return None

        target = target.strip('<').strip('>')
        target = '_'.join(target.split(' ')[:-1])

        coll = {}
        for m in sys.modules.values():
            for sym in dir(m):
                o = getattr (m, sym)
                if type(o) is types.ClassType:
                    name = '_'.join(repr(o).strip('<').strip('>').split(' ')[:-1])
                    coll[name] = o

        self._target = coll.get(target, None)
        return self._target



    def view_backref(self):
        if self.target is None:
            return "Please select an item to introspect"
        return self.back_ref_file


    def view_ref(self):
        if self.target is None:
            return "Please select an item to introspect"
        return self.ref_file


    @property
    def ref_file(self):
        self.request.response.setHeader('content-type','image/png')
        f = NamedTemporaryFile('wb', suffix='.png')
        checks.show_refs([self.target], max_depth=6, filename=f.name)
        return open(f.name,'r').read()

    @property
    def back_ref_file(self):
        self.request.response.setHeader('content-type','image/png')
        f = NamedTemporaryFile('wb', suffix='.png')
        checks.show_backrefs([self.target], max_depth=6, filename=f.name)
        return open(f.name,'r').read()


    def context_refs(self):
        self._target = self.context
        return self.ref_file

    def context_backrefs(self):
        self._target = self.context
        return self.back_ref_file

    def reset_heap(self):
        # Resets for testing
        heapy.setrelheap()

    def memory(self):
        return pprint.pformat(heapy.heap())

    # Print relative memory consumption since last sycle
    def relative_memory(self):
        res = pprint.pformat(heapy.heap())
        heapy.setref()
        return res

    def by_referrers(self):
        res = pprint.pformat(heapy.heap().byrcs)
        return res

    def get_biggest_offender(self):
        obj = heapy.heap()[0].byrcs[0].referrers.byrcs
        res = "SIZE: %s\n\n" % obj.domisize
        res += pprint.pformat(obj)
        return res

    # Print relative memory consumption w/heap traversing
    def traverse_relative_memory(self):
        res = pprint.pformat(heapy.heap().get_rp(40))
        heapy.setref()
        return res

    def breakpoint(self):
        import pdb; pdb.set_trace()
        obj = heapy.heap()
        return "done"

##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################

__version__='$Revision: 1.61 $'[11:-2]

import re, sys, os,  urllib, time, whrandom, cgi
from BaseRequest import BaseRequest
from HTTPResponse import HTTPResponse
from cgi import FieldStorage, escape
from urllib import quote, unquote, splittype, splitport
from Converters import get_converter
from maybe_lock import allocate_lock
xmlrpc=None # Placeholder for module that we'll import if we have to.

#cgi hotfix:
if not hasattr(cgi, 'valid_boundary'):
    import cgi_hotfix

isCGI_NAME = {
        'SERVER_SOFTWARE' : 1, 
        'SERVER_NAME' : 1, 
        'GATEWAY_INTERFACE' : 1, 
        'SERVER_PROTOCOL' : 1, 
        'SERVER_PORT' : 1, 
        'REQUEST_METHOD' : 1, 
        'PATH_INFO' : 1, 
        'PATH_TRANSLATED' : 1, 
        'SCRIPT_NAME' : 1, 
        'QUERY_STRING' : 1, 
        'REMOTE_HOST' : 1, 
        'REMOTE_ADDR' : 1, 
        'AUTH_TYPE' : 1, 
        'REMOTE_USER' : 1, 
        'REMOTE_IDENT' : 1, 
        'CONTENT_TYPE' : 1, 
        'CONTENT_LENGTH' : 1,
        'SERVER_URL': 1,
        }.has_key

hide_key={'HTTP_AUTHORIZATION':1,
          'HTTP_CGI_AUTHORIZATION': 1,
          }.has_key

default_port={'http': '80', 'https': '443'}

_marker=[]
class HTTPRequest(BaseRequest):
    """\
    Model HTTP request data.
    
    This object provides access to request data.  This includes, the
    input headers, form data, server data, and cookies.

    Request objects are created by the object publisher and will be
    passed to published objects through the argument name, REQUEST.

    The request object is a mapping object that represents a
    collection of variable to value mappings.  In addition, variables
    are divided into five categories:

      - Environment variables

        These variables include input headers, server data, and other
        request-related data.  The variable names are as <a
        href="http://hoohoo.ncsa.uiuc.edu/cgi/env.html">specified</a>
        in the <a
        href="http://hoohoo.ncsa.uiuc.edu/cgi/interface.html">CGI
        specification</a>

      - Form data

        These are data extracted from either a URL-encoded query
        string or body, if present.

      - Cookies

        These are the cookie data, if present.

      - Lazy Data

        These are callables which are deferred until explicitly
        referenced, at which point they are resolved and stored as
        application data.

      - Other

        Data that may be set by an application object.

    The form attribute of a request is actually a Field Storage
    object.  When file uploads are used, this provides a richer and
    more complex interface than is provided by accessing form data as
    items of the request.  See the FieldStorage class documentation
    for more details.

    The request object may be used as a mapping object, in which case
    values will be looked up in the order: environment variables,
    other variables, form data, and then cookies.
    """
    _hacked_path=None
    args=()
    _file=None
    _urls = ()

    retry_max_count=3
    def supports_retry(self):
        if self.retry_count < self.retry_max_count:
            time.sleep(whrandom.uniform(0, 2**(self.retry_count)))
            return 1

    def retry(self):
        self.retry_count=self.retry_count+1
        self.stdin.seek(0)
        r=self.__class__(stdin=self.stdin,
                         environ=self._orig_env,
                         response=self.response.retry()
                         )
        r.retry_count=self.retry_count
        return r

    def close(self):
        # we want to clear the lazy dict here because BaseRequests don't have
        # one.  Without this, there's the possibility of memory leaking
        # after every request.
        self._lazies = {}
        BaseRequest.close(self)

    def setServerURL(self, protocol=None, hostname=None, port=None):
        """ Set the parts of generated URLs. """
        other = self.other
        server_url = other.get('SERVER_URL', '')
        if protocol is None and hostname is None and port is None:
            return server_url
        oldprotocol, oldhost = splittype(server_url)
        oldhostname, oldport = splitport(oldhost[2:])
        if protocol is None: protocol = oldprotocol
        if hostname is None: hostname = oldhostname
        if port is None: port = oldport
        
        if (port is None or default_port[protocol] == port):
            host = hostname
        else:
            host = hostname + ':' + port
        server_url = other['SERVER_URL'] = '%s://%s' % (protocol, host)
        self._resetURLS()
        return server_url

    def setVirtualRoot(self, path, hard=0):
        """ Treat the current publishing object as a VirtualRoot """
        other = self.other
        if type(path) is type(''):
            path = filter(None, path.split( '/'))
        self._script[:] = map(quote, path)
        del self._steps[:]
        parents = other['PARENTS']
        if hard:
            del parents[:-1]
        other['VirtualRootPhysicalPath'] = parents[-1].getPhysicalPath()
        self._resetURLS()

    def physicalPathToVirtualPath(self, path):
        """ Remove the path to the VirtualRoot from a physical path """
        if type(path) is type(''):
            path = path.split( '/')
        rpp = self.other.get('VirtualRootPhysicalPath', ('',))
        i = 0
        for name in rpp[:len(path)]:
            if path[i] == name:
                i = i + 1
            else:
                break
        return path[i:]

    def physicalPathToURL(self, path, relative=0):
        """ Convert a physical path into a URL in the current context """
        path = self._script + map(quote, self.physicalPathToVirtualPath(path))
        if relative:
            path.insert(0, '')
        else:
            path.insert(0, self['SERVER_URL'])
        return '/'.join(path)

    def physicalPathFromURL(self, URL):
        """ Convert a URL into a physical path in the current context.
            If the URL makes no sense in light of the current virtual
            hosting context, a ValueError is raised."""
        other = self.other
        bad_server_url = 0
        path = filter(None, URL.split( '/'))

        if URL.find( '://') >= 0:
            path = path[2:]

        # Check the path against BASEPATH1
        vhbase = self._script
        vhbl = len(vhbase)
        bad_basepath = 0
        if path[:vhbl] == vhbase:
            path = path[vhbl:]
        else:
            raise ValueError, (
                'Url does not match virtual hosting context'
                )
        vrpp = other.get('VirtualRootPhysicalPath', ('',))
        return list(vrpp) + map(unquote, path)

    def _resetURLS(self):
        other = self.other
        other['URL'] = '/'.join([other['SERVER_URL']] + self._script +
                            self._steps)
        for x in self._urls:
            del self.other[x]
        self._urls = ()

    def __init__(self, stdin, environ, response, clean=0):
        self._orig_env=environ
        # Avoid the overhead of scrubbing the environment in the
        # case of request cloning for traversal purposes. If the
        # clean flag is set, we know we can use the passed in
        # environ dict directly.
        if not clean: environ=sane_environment(environ)

        if environ.has_key('HTTP_AUTHORIZATION'):
            self._auth=environ['HTTP_AUTHORIZATION']
            response._auth=1
            del environ['HTTP_AUTHORIZATION']

        self.stdin=stdin
        self.environ=environ
        have_env=environ.has_key
        get_env=environ.get
        self.response=response
        other=self.other={'RESPONSE': response}
        self.form={}
        self.steps=[]
        self._steps=[]
        self._lazies={}

        ################################################################
        # Get base info first. This isn't likely to cause
        # errors and might be useful to error handlers.
        b=script=get_env('SCRIPT_NAME','').strip()

        # _script and the other _names are meant for URL construction
        self._script = map(quote, filter(None, script.split( '/')))
        
        while b and b[-1]=='/': b=b[:-1]
        p = b.rfind('/')
        if p >= 0: b=b[:p+1]
        else: b=''
        while b and b[0]=='/': b=b[1:]

        server_url=get_env('SERVER_URL',None)
        if server_url is not None:
             other['SERVER_URL'] = server_url = server_url.strip()
        else:
             if have_env('HTTPS') and (
                 environ['HTTPS'] == "on" or environ['HTTPS'] == "ON"):
                 protocol = 'https'
             elif (have_env('SERVER_PORT_SECURE') and 
                   environ['SERVER_PORT_SECURE'] == "1"):
                 protocol = 'https'
             else: protocol = 'http'

             if have_env('HTTP_HOST'):
                 host = environ['HTTP_HOST'].strip()
                 hostname, port = splitport(host)

                 # NOTE: some (DAV) clients manage to forget the port. This
                 # can be fixed with the commented code below - the problem
                 # is that it causes problems for virtual hosting. I've left
                 # the commented code here in case we care enough to come
                 # back and do anything with it later.
                 #
                 # if port is None and environ.has_key('SERVER_PORT'):
                 #     s_port=environ['SERVER_PORT']
                 #     if s_port not in ('80', '443'):
                 #         port=s_port

             else:
                 hostname = environ['SERVER_NAME'].strip()
                 port = environ['SERVER_PORT']
             self.setServerURL(protocol=protocol, hostname=hostname, port=port)
             server_url = other['SERVER_URL']
             
        if server_url[-1:]=='/': server_url=server_url[:-1]
                        
        if b: self.base="%s/%s" % (server_url,b)
        else: self.base=server_url
        while script[:1]=='/': script=script[1:]
        if script: script="%s/%s" % (server_url,script)
        else:      script=server_url
        other['URL']=self.script=script

        ################################################################
        # Cookie values should *not* be appended to existing form
        # vars with the same name - they are more like default values
        # for names not otherwise specified in the form.
        cookies={}
        k=get_env('HTTP_COOKIE','')
        if k:
            parse_cookie(k, cookies)
            for k,item in cookies.items():
                if not other.has_key(k):
                    other[k]=item
        self.cookies=cookies
    
    def processInputs(
        self,
        # "static" variables that we want to be local for speed
        SEQUENCE=1,
        DEFAULT=2,
        RECORD=4,
        RECORDS=8,
        REC=12, # RECORD|RECORDS
        EMPTY=16,
        CONVERTED=32,
        hasattr=hasattr,
        getattr=getattr,
        setattr=setattr,
        search_type=re.compile('(:[a-zA-Z][a-zA-Z0-9_]+|\\.[xy])$').search,
        ):
        """Process request inputs

        We need to delay input parsing so that it is done under
        publisher control for error handling purposes.
        """
        response=self.response
        environ=self.environ
        method=environ.get('REQUEST_METHOD','GET')
        
        if method != 'GET': fp=self.stdin
        else:               fp=None

        form=self.form
        other=self.other

        meth=None
        fs=FieldStorage(fp=fp,environ=environ,keep_blank_values=1)
        if not hasattr(fs,'list') or fs.list is None:
            # Hm, maybe it's an XML-RPC
            if (fs.headers.has_key('content-type') and
                fs.headers['content-type'] == 'text/xml' and
                method == 'POST'):
                # Ye haaa, XML-RPC!
                global xmlrpc
                if xmlrpc is None: import xmlrpc
                meth, self.args = xmlrpc.parse_input(fs.value)
                response=xmlrpc.response(response)
                other['RESPONSE']=self.response=response
                other['REQUEST_METHOD']='' # We don't want index_html!
                self.maybe_webdav_client = 0
            else:
                self._file=fs.file
        else:
            fslist=fs.list
            tuple_items={}
            lt=type([])
            CGI_name=isCGI_NAME
            defaults={}
            converter=seqf=None
            
            for item in fslist:
                
                key=item.name
                if (hasattr(item,'file') and hasattr(item,'filename')
                    and hasattr(item,'headers')):
                    if (item.file and
                        (item.filename is not None
                         # RFC 1867 says that all fields get a content-type.
                         # or 'content-type' in map(lower, item.headers.keys())
                         )):
                        item=FileUpload(item)
                    else:
                        item=item.value

                flags=0

                # Loop through the different types and set
                # the appropriate flags

                # We'll search from the back to the front.
                # We'll do the search in two steps.  First, we'll
                # do a string search, and then we'll check it with
                # a re search.
                

                l=key.rfind(':')
                if l >= 0:
                    mo = search_type(key,l)
                    if mo: l=mo.start(0)
                    else:  l=-1

                    while l >= 0:
                        type_name=key[l+1:]
                        key=key[:l]
                        c=get_converter(type_name, None)
                        
                        if c is not None: 
                            converter=c
                            flags=flags|CONVERTED
                        elif type_name == 'list':
                            seqf=list
                            flags=flags|SEQUENCE
                        elif type_name == 'tuple':
                            seqf=tuple
                            tuple_items[key]=1
                            flags=flags|SEQUENCE
                        elif (type_name == 'method' or type_name == 'action'):
                            if l: meth=key
                            else: meth=item
                        elif (type_name == 'default_method' or type_name == \
                              'default_action'):
                            if not meth:
                                if l: meth=key
                                else: meth=item
                        elif type_name == 'default':
                            flags=flags|DEFAULT
                        elif type_name == 'record':
                            flags=flags|RECORD
                        elif type_name == 'records':
                            flags=flags|RECORDS
                        elif type_name == 'ignore_empty':
                            if not item: flags=flags|EMPTY
    
                        l=key.rfind(':')
                        if l < 0: break
                        mo=search_type(key,l)
                        if mo: l = mo.start(0)
                        else:  l = -1


             
                # Filter out special names from form:
                if CGI_name(key) or key[:5]=='HTTP_': continue

                if flags:

                    # skip over empty fields    
                    if flags&EMPTY: continue

                    #Split the key and its attribute
                    if flags&REC:
                        key=key.split(".")
                        key, attr=".".join(key[:-1]), key[-1]
                       
                    # defer conversion
                    if flags&CONVERTED:
                        try:
                            item=converter(item)
                        except:
                            if (not item and not (flags&DEFAULT) and
                                defaults.has_key(key)):
                                item = defaults[key]
                                if flags&RECORD:
                                    item=getattr(item,attr)
                                if flags&RECORDS:
                                    item.reverse()
                                    item = item[0]
                                    item=getattr(item,attr)
                            else:
                                raise                            
                         
                    #Determine which dictionary to use
                    if flags&DEFAULT:
                       mapping_object = defaults
                    else:
                       mapping_object = form

                    #Insert in dictionary
                    if mapping_object.has_key(key):
                       if flags&RECORDS:
                           #Get the list and the last record
                           #in the list
                           reclist = mapping_object[key]
                           reclist.reverse()
                           x=reclist[0]
                           reclist.reverse()
                           if not hasattr(x,attr):
                               #If the attribute does not
                               #exist, setit
                               if flags&SEQUENCE: item=[item]
                               reclist.remove(x)
                               setattr(x,attr,item)
                               reclist.append(x)
                               mapping_object[key] = reclist
                           else:
                               if flags&SEQUENCE:
                                   # If the attribute is a
                                   # sequence, append the item
                                   # to the existing attribute
                                   reclist.remove(x)
                                   y = getattr(x, attr)
                                   y.append(item)
                                   setattr(x, attr, y)
                                   reclist.append(x)
                                   mapping_object[key] = reclist
                               else:
                                   # Create a new record and add
                                   # it to the list
                                   n=record()
                                   setattr(n,attr,item)
                                   reclist.append(n)
                                   mapping_object[key]=reclist
                       elif flags&RECORD:
                           b=mapping_object[key]
                           if flags&SEQUENCE:
                              item=[item]
                              if not hasattr(b,attr):
                                  # if it does not have the
                                  # attribute, set it
                                  setattr(b,attr,item)
                              else:
                                  # it has the attribute so
                                  # append the item to it
                                  setattr(b,attr,getattr(b,attr)+item)
                           else:
                              # it is not a sequence so
                              # set the attribute
                              setattr(b,attr,item)        
                       else:
                          # it is not a record or list of records
                           found=mapping_object[key]
                           if type(found) is lt:
                               found.append(item)
                           else:
                               found=[found,item]
                               mapping_object[key]=found
                    else:
                       # The dictionary does not have the key
                       if flags&RECORDS:
                           # Create a new record, set its attribute
                           # and put it in the dictionary as a list
                           a = record()
                           if flags&SEQUENCE: item=[item]
                           setattr(a,attr,item)
                           mapping_object[key]=[a]
                       elif flags&RECORD:
                           # Create a new record, set its attribute
                           # and put it in the dictionary
                           if flags&SEQUENCE: item=[item]
                           r = mapping_object[key]=record()
                           setattr(r,attr,item)
                       else:
                           # it is not a record or list of records
                           if flags&SEQUENCE: item=[item]
                           mapping_object[key]=item

                else:
                    # This branch is for case when no type was specified.
                    mapping_object = form
    
                    #Insert in dictionary
                    if mapping_object.has_key(key):
                        # it is not a record or list of records
                        found=mapping_object[key]
                        if type(found) is lt:
                            found.append(item)
                        else:
                            found=[found,item]
                            mapping_object[key]=found
                    else:
                        mapping_object[key]=item

            #insert defaults into form dictionary
            if defaults:
                for keys, values in defaults.items():
                    if not form.has_key(keys):
                        # if the form does not have the key,
                        # set the default
                        form[keys]=values
                    else:
                        #The form has the key
                        if getattr(values, '__class__',0) is record:
                           # if the key is mapped to a record, get the
                           # record
                           r = form[keys]
                           for k, v in values.__dict__.items():
                              # loop through the attributes and values
                              # in the default dictionary
                              if not hasattr(r, k):
                                 # if the form dictionary doesn't have
                                 # the attribute, set it to the default
                                 setattr(r,k,v)
                                 form[keys] = r    
                        elif values == type([]):
                               # the key is mapped to a list
                               l = form[keys]
                               for x in values:
                                   # for each x in the list
                                   if getattr(x, '__class__',0) is record:
                                       # if the x is a record
                                       for k, v in x.__dict__.items():
                                           
                                           # loop through each
                                           # attribute and value in
                                           # the record
                                           
                                           for y in l:
                                               
                                               # loop through each
                                               # record in the form
                                               # list if it doesn't
                                               # have the attributes
                                               # in the default
                                               # dictionary, set them
                                               
                                               if not hasattr(y, k):
                                                   setattr(y, k, v)
                                   else:
                                       # x is not a record
                                       if not a in l:
                                           l.append(a)
                               form[keys] = l
                        else:
                            # The form has the key, the key is not mapped
                            # to a record or sequence so do nothing
                            pass
                                
            # Convert to tuples
            if tuple_items:
                for key in tuple_items.keys():
                   # Split the key and get the attr
                   k=key.split( ".")
                   k,attr='.'.join(k[:-1]), k[-1]
                   a = attr
                   # remove any type_names in the attr
                   while not a=='':
                      a=a.split( ":")
                      a,new=':'.join(a[:-1]), a[-1]
                   attr = new
                   if form.has_key(k):
                      # If the form has the split key get its value
                      item =form[k]
                      if (hasattr(item, '__class__') and
                          item.__class__ is record):
                         # if the value is mapped to a record, check if it
                         # has the attribute, if it has it, convert it to
                         # a tuple and set it
                         if hasattr(item,attr):
                            value=tuple(getattr(item,attr))
                            setattr(item,attr,value)
                      else:
                         # It is mapped to a list of  records
                         for x in item:
                            # loop through the records
                            if hasattr(x, attr):
                               # If the record has the attribute
                               # convert it to a tuple and set it
                               value=tuple(getattr(x,attr))
                               setattr(x,attr,value)          
                   else:
                      # the form does not have the split key 
                      if form.has_key(key):
                         # if it has the original key, get the item
                         # convert it to a tuple
                         item=form[key]  
                         item=tuple(form[key])
                         form[key]=item
                     
        other.update(form)
        if meth:
            if environ.has_key('PATH_INFO'):
                path=environ['PATH_INFO']
                while path[-1:]=='/': path=path[:-1]
            else: path=''
            other['PATH_INFO']=path="%s/%s" % (path,meth)
            self._hacked_path=1

    def resolve_url(self, url):
        # Attempt to resolve a url into an object in the Zope
        # namespace. The url must be a fully-qualified url. The
        # method will return the requested object if it is found
        # or raise the same HTTP error that would be raised in
        # the case of a real web request. If the passed in url
        # does not appear to describe an object in the system
        # namespace (e.g. the host, port or script name dont
        # match that of the current request), a ValueError will
        # be raised.
        if url.find(self.script) != 0:
            raise ValueError, 'Different namespace.'
        path=url[len(self.script):]
        while path and path[0]=='/':  path=path[1:]
        while path and path[-1]=='/': path=path[:-1]
        req=self.clone()
        rsp=req.response
        req['PATH_INFO']=path
        object=None
        
        # Try to traverse to get an object. Note that we call
        # the exception method on the response, but we don't
        # want to actually abort the current transaction
        # (which is usually the default when the exception
        # method is called on the response).
        try: object=req.traverse(path)
        except: rsp.exception()
        if object is None:
            req.close()
            raise rsp.errmsg, sys.exc_info()[1]

        # The traversal machinery may return a "default object"
        # like an index_html document. This is not appropriate
        # in the context of the resolve_url method so we need
        # to ensure we are getting the actual object named by
        # the given url, and not some kind of default object.
        if hasattr(object, 'id'):
            if callable(object.id):
                name=object.id()
            else: name=object.id
        elif hasattr(object, '__name__'):
            name=object.__name__
        else: name=''
        if name != os.path.split(path)[-1]:
            object=req.PARENTS[0]

        req.close()
        return object
        

    def clone(self):
        # Return a clone of the current request object 
        # that may be used to perform object traversal.
        environ=self.environ.copy()
        environ['REQUEST_METHOD']='GET'
        if self._auth: environ['HTTP_AUTHORIZATION']=self._auth
        clone=HTTPRequest(None, environ, HTTPResponse(), clean=1)
        clone['PARENTS']=[self['PARENTS'][-1]]
        return clone

    def get_header(self, name, default=None):
        """Return the named HTTP header, or an optional default
        argument or None if the header is not found. Note that
        both original and CGI-ified header names are recognized,
        e.g. 'Content-Type', 'CONTENT_TYPE' and 'HTTP_CONTENT_TYPE'
        should all return the Content-Type header, if available.
        """
        environ=self.environ
        name=('_'.join(name.split("-"))).upper()
        val=environ.get(name, None)
        if val is not None:
            return val
        if name[:5] != 'HTTP_':
            name='HTTP_%s' % name
        return environ.get(name, default)

    def get(self, key, default=None,
            URLmatch=re.compile('URL(PATH)?([0-9]+)$').match,
            BASEmatch=re.compile('BASE(PATH)?([0-9]+)$').match,
            ):
        """Get a variable value

        Return a value for the required variable name.
        The value will be looked up from one of the request data
        categories. The search order is environment variables,
        other variables, form data, and then cookies. 
        
        """ #"
        other=self.other
        if other.has_key(key):
            if key=='REQUEST': return self
            return other[key]

        if key[:1]=='U':
            match = URLmatch(key)
            if match is not None:
                pathonly, n = match.groups()
                path = self._script + self._steps
                n = len(path) - int(n)
                if n < 0:
                    raise KeyError, key
                if pathonly:
                    path = [''] + path[:n]
                else:
                    path = [other['SERVER_URL']] + path[:n]
                other[key] = URL = '/'.join(path)
                self._urls = self._urls + (key,)
                return URL

        if isCGI_NAME(key) or key[:5] == 'HTTP_':
            environ=self.environ
            if environ.has_key(key) and (not hide_key(key)):
                return environ[key]
            return ''

        if key=='REQUEST': return self

        if key[:1]=='B':
            match = BASEmatch(key)
            if match is not None:
                pathonly, n = match.groups()
                path = self._steps
                n = int(n)
                if n:
                    n = n - 1
                    if len(path) < n:
                        raise KeyError, key

                    v = self._script + path[:n]
                else:
                    v = self._script[:-1]
                if pathonly:
                    v.insert(0, '')
                else:
                    v.insert(0, other['SERVER_URL'])
                other[key] = URL = '/'.join(v)
                self._urls = self._urls + (key,)
                return URL

            if key=='BODY' and self._file is not None:
                p=self._file.tell()
                self._file.seek(0)
                v=self._file.read()
                self._file.seek(p)
                self.other[key]=v
                return v

            if key=='BODYFILE' and self._file is not None:
                v=self._file
                self.other[key]=v
                return v

        v=self.common.get(key, _marker)
        if v is not _marker: return v

        if self._lazies:
            v = self._lazies.get(key, _marker)
            if v is not _marker:
                if callable(v): v = v()
                self[key] = v                   # Promote lazy value
                del self._lazies[key]
                return v

        return default

    def __getitem__(self, key, default=_marker):
        v = self.get(key, default)
        if v is _marker:
            raise KeyError, key
        return v

    def __getattr__(self, key, default=_marker):
        v = self.get(key, default)
        if v is _marker:
            raise AttributeError, key
        return v

    def set_lazy(self, key, callable):
        self._lazies[key] = callable

    def has_key(self, key):
        try: self[key]
        except: return 0
        else: return 1

    def keys(self):
        keys = {}
        keys.update(self.common)
        keys.update(self._lazies)

        for key in self.environ.keys():
            if (isCGI_NAME(key) or key[:5] == 'HTTP_') and \
               (not hide_key(key)):
                    keys[key] = 1

        n=0
        while 1:
            n=n+1
            key = "URL%s" % n
            if not self.has_key(key): break

        n=0
        while 1:
            n=n+1
            key = "BASE%s" % n
            if not self.has_key(key): break

        keys.update(self.other)

        keys=keys.keys()
        keys.sort()

        return keys

    def __str__(self):
        result="<h3>form</h3><table>"
        row='<tr valign="top" align="left"><th>%s</th><td>%s</td></tr>'
        for k,v in self.form.items():
            result=result + row % (escape(k), escape(repr(v)))
        result=result+"</table><h3>cookies</h3><table>"
        for k,v in self.cookies.items():
            result=result + row % (escape(k), escape(repr(v)))
        result=result+"</table><h3>lazy items</h3><table>"
        for k,v in self._lazies.items():
            result=result + row % (escape(k), escape(repr(v)))
        result=result+"</table><h3>other</h3><table>"
        for k,v in self.other.items():
            if k in ('PARENTS','RESPONSE'): continue
            result=result + row % (escape(k), escape(repr(v)))
    
        for n in "0123456789":
            key = "URL%s"%n
            try: result=result + row % (key, escape(self[key])) 
            except KeyError: pass
        for n in "0123456789":
            key = "BASE%s"%n
            try: result=result + row % (key, escape(self[key])) 
            except KeyError: pass

        result=result+"</table><h3>environ</h3><table>"
        for k,v in self.environ.items():
            if not hide_key(k):
                result=result + row % (escape(k), escape(repr(v)))
        return result+"</table>"

    __repr__=__str__

    def text(self):
        result="FORM\n\n"
        row='%-20s %s\n'
        for k,v in self.form.items():
            result=result + row % (k, repr(v))
        result=result+"\nCOOKIES\n\n"
        for k,v in self.cookies.items():
            result=result + row % (k, repr(v))
        result=result+"\nLAZY ITEMS\n\n"
        for k,v in self._lazies.items():
            result=result + row % (k, repr(v))
        result=result+"\nOTHER\n\n"
        for k,v in self.other.items():
            if k in ('PARENTS','RESPONSE'): continue
            result=result + row % (k, repr(v))
    
        for n in "0123456789":
            key = "URL%s"%n
            try: result=result + row % (key, self[key]) 
            except KeyError: pass
        for n in "0123456789":
            key = "BASE%s"%n
            try: result=result + row % (key, self[key]) 
            except KeyError: pass

        result=result+"\nENVIRON\n\n"
        for k,v in self.environ.items():
            if not hide_key(k):
                result=result + row % (k, v)
        return result

    def _authUserPW(self):
        global base64
        auth=self._auth
        if auth:
            if auth[:6].lower() == 'basic ':
                if base64 is None: import base64
                [name,password] = \
                    base64.decodestring(auth.split()[-1]).split(':')
                return name, password




base64=None

def sane_environment(env):
    # return an environment mapping which has been cleaned of
    # funny business such as REDIRECT_ prefixes added by Apache
    # or HTTP_CGI_AUTHORIZATION hacks.
    dict={}
    for key, val in env.items():
        while key[:9]=='REDIRECT_':
            key=key[9:]
        dict[key]=val
    if dict.has_key('HTTP_CGI_AUTHORIZATION'):
        dict['HTTP_AUTHORIZATION']=dict['HTTP_CGI_AUTHORIZATION']
        try: del dict['HTTP_CGI_AUTHORIZATION']
        except: pass
    return dict


def str_field(v):
    if type(v) is ListType:
        return map(str_field,v)

    if hasattr(v,'__class__') and v.__class__ is FieldStorage:
        v=v.value
    elif type(v) is not StringType:
        if hasattr(v,'file') and v.file: v=v.file
        elif hasattr(v,'value'): v=v.value
    return v


class FileUpload:
    '''\
    File upload objects

    File upload objects are used to represent file-uploaded data.

    File upload objects can be used just like files.

    In addition, they have a 'headers' attribute that is a dictionary
    containing the file-upload headers, and a 'filename' attribute
    containing the name of the uploaded file.
    '''

    # Allow access to attributes such as headers and filename so
    # that ZClass authors can use DTML to work with FileUploads.
    __allow_access_to_unprotected_subobjects__=1

    def __init__(self, aFieldStorage):

        file=aFieldStorage.file
        if hasattr(file, '__methods__'): methods=file.__methods__
        else: methods= ['close', 'fileno', 'flush', 'isatty',
                        'read', 'readline', 'readlines', 'seek',
                        'tell', 'truncate', 'write', 'writelines']

        d=self.__dict__
        for m in methods:
            if hasattr(file,m): d[m]=getattr(file,m)

        self.headers=aFieldStorage.headers
        self.filename=aFieldStorage.filename

        # Add an assertion to the rfc822.Message object that implements
        # self.headers so that managed code can access them.
        try:    self.headers.__allow_access_to_unprotected_subobjects__ = 1
        except: pass


parse_cookie_lock=allocate_lock()
def parse_cookie(text,
                 result=None,
                 qparmre=re.compile(
                    '([\x00- ]*([^\x00- ;,="]+)="([^"]*)"([\x00- ]*[;,])?[\x00- ]*)'),
                 parmre=re.compile(
                    '([\x00- ]*([^\x00- ;,="]+)=([^\x00- ;,"]*)([\x00- ]*[;,])?[\x00- ]*)'),

                 acquire=parse_cookie_lock.acquire,
                 release=parse_cookie_lock.release,
                 ):

    if result is None: result={}
    already_have=result.has_key

    acquire()
    try:

        mo_q = qparmre.match(text)

        if mo_q:
            # Match quoted correct cookies

            l     = len(mo_q.group(1))
            name  = mo_q.group(2)
            value = mo_q.group(3)

        else:
            # Match evil MSIE cookies ;)

            mo_p = parmre.match(text)

            if mo_p:
                l     = len(mo_p.group(1))
                name  = mo_p.group(2)
                value = mo_p.group(3)

            else: 
                return result 

    finally: release()

    if not already_have(name): result[name]=value

    return apply(parse_cookie,(text[l:],result))

# add class
class record:

    # Allow access to record methods and values from DTML
    __allow_access_to_unprotected_subobjects__=1

    def __getattr__(self, key, default=None):
        if key in ('get', 'keys', 'items', 'values', 'copy', 'has_key'):
            return getattr(self.__dict__, key)
        raise AttributeError, key

    def __getitem__(self, key):
        return self.__dict__[key]
            
    def __str__(self):
        L1 = self.__dict__.items()
        L1.sort()
        return ", ".join(map(lambda item: "%s: %s" % item, L1)) 

    def __repr__(self):
        L1 = self.__dict__.items()
        L1.sort()
        return ', '.join(
            map(lambda item: "%s: %s" % (item[0], repr(item[1])), L1))

# Flags
SEQUENCE=1
DEFAULT=2
RECORD=4
RECORDS=8
REC=RECORD|RECORDS
EMPTY=16
CONVERTED=32


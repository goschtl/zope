##############################################################################
#
# Zope Public License (ZPL) Version 0.9.5
# ---------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Any use, including use of the Zope software to operate a website,
#    must either comply with the terms described below under
#    "Attribution" or alternatively secure a separate license from
#    Digital Creations.  Digital Creations will not unreasonably
#    deny such a separate license in the event that the request
#    explains in detail a valid reason for withholding attribution.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# Attribution
# 
#   Individuals or organizations using this software as a web site must
#   provide attribution by placing the accompanying "button" and a link
#   to the accompanying "credits page" on the website's main entry
#   point.  In cases where this placement of attribution is not
#   feasible, a separate arrangment must be concluded with Digital
#   Creations.  Those using the software for purposes other than web
#   sites must provide a corresponding attribution in locations that
#   include a copyright using a manner best suited to the application
#   environment.  Where attribution is not possible, or is considered
#   to be onerous for some other reason, a request should be made to
#   Digital Creations to waive this requirement in writing.  As stated
#   above, for valid requests, Digital Creations will not unreasonably
#   deny such requests.
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################
__doc__='''Database Connection

$Id: DABase.py,v 1.5 1998/12/16 15:28:47 jim Exp $'''
__version__='$Revision: 1.5 $'[11:-2]

from db import manage_DataSources
import Shared.DC.ZRDB.Connection, sys
from Globals import HTMLFile
from ImageFile import ImageFile
from ExtensionClass import Base
import Acquisition

class Connection(Shared.DC.ZRDB.Connection.Connection):
    _isAnSQLConnection=1

    manage_options=Shared.DC.ZRDB.Connection.Connection.manage_options+(
        {'label': 'Browse', 'action':'manage_browse'},
        # {'label': 'Design', 'action':'manage_tables'},
        )

    manage_tables=HTMLFile('tables',globals())
    manage_browse=HTMLFile('browse',globals())

    info=None
        
    def tpValues(self):
        if hasattr(self, '_v_tpValues'): return self._v_tpValues
        r=[]
        self._v_tables=tables=TableBrowserCollection()
        tables=tables.__dict__
        c=self._v_database_connection
        try:
            for d in c.tables(rdb=0):
                try:
                    name=d['TABLE_NAME']
                    b=TableBrowser()
                    b._d=d
                    b._columns=c.columns(name)
                    try: b.icon=table_icons[d['TABLE_TYPE']]
                    except: pass
                    r.append(b)
                    tables[name]=b
                except:
                    # print d['TABLE_NAME'], sys.exc_type, sys.exc_value
                    pass

        finally: pass #print sys.exc_type, sys.exc_value
        self._v_tpValues=r
        return r

    def __getitem__(self, name):
        if name=='tableNamed':
            if not hasattr(self, '_v_tables'): self.tpValues()
            return self._v_tables.__of__(self)
        raise KeyError, name

    def manage_wizard(self, tables):
        " "

    def manage_join(self, tables, select_cols, join_cols, REQUEST=None):
        """Create an SQL join"""

    def manage_insert(self, table, cols, REQUEST=None):
        """Create an SQL insert"""

    def manage_update(self, table, keys, cols, REQUEST=None):
        """Create an SQL update"""

class TableBrowserCollection(Acquisition.Implicit):
    "Helper class for accessing tables via URLs"

class Browser(Base):
    def __getattr__(self, name):
        try: return self._d[name]
        except KeyError: raise AttributeError, name

class TableBrowser(Browser, Acquisition.Implicit):
    icon='what'
    Description=check=''
    info=HTMLFile('table_info',globals())
    menu=HTMLFile('table_menu',globals())

    def tpValues(self):
        r=[]
        for d in self._columns:
            b=ColumnBrowser()
            b._d=d
            try: b.icon=field_icons[d['Type']]
            except: pass
            b.TABLE_NAME=self._d['TABLE_NAME']
            r.append(b)
        return r
            
    def tpId(self): return self._d['TABLE_NAME']
    def tpURL(self): return "Table/%s" % self._d['TABLE_NAME']
    def Name(self): return self._d['TABLE_NAME']
    def Type(self): return self._d['TABLE_TYPE']

    manage_designInput=HTMLFile('designInput',globals())
    def manage_buildInput(self, id, source, default, REQUEST=None):
        "Create a database method for an input form"
        args=[]
        values=[]
        names=[]
        columns=self._columns
        for i in range(len(source)):
            s=source[i]
            if s=='Null': continue
            c=columns[i]
            d=default[i]
            t=c['Type']
            n=c['Name']
            names.append(n)
            if s=='Argument':
                values.append("<!--#sql-value %s type=%s-->'" %
                              (n, vartype(t)))
                a='%s%s' % (n, boboType(t))
                if d: a="%s=%s" % (a,d)
                args.append(a)
            elif s=='Property':
                values.append("<!--#sql-value %s type=%s-->'" %
                              (n, vartype(t)))
            else:
                if isStringType(t):
                    if find(d,"\'") >= 0: d=join(split(d,"\'"),"''")
                    values.append("'%s'" % d)
                elif d:
                    values.append(str(d))
                else:
                    raise ValueError, (
                        'no default was given for <em>%s</em>' % n)

            
            

class ColumnBrowser(Browser):
    icon='field'

    def check(self):
        return ('\t<input type=checkbox name="%s.%s">' %
                (self.TABLE_NAME, self._d['Name']))
    def tpId(self): return self._d['Name']
    def tpURL(self): return "Column/%s" % self._d['Name']
    def Description(self):
        d=self._d
        if d['Scale']:
            return " %(Type)s(%(Precision)s,%(Scale)s) %(Nullable)s" % d
        else:
            return " %(Type)s(%(Precision)s) %(Nullable)s" % d

table_icons={
    'TABLE': 'table',
    'VIEW':'view',
    'SYSTEM_TABLE': 'stable',
    }

field_icons={
    'BIGINT': 'int',
    'BINARY': 'bin',
    'BIT': 'bin',
    'CHAR': 'text',
    'DATE': 'date',
    'DECIMAL': 'float',
    'DOUBLE': 'float',
    'FLOAT': 'float',
    'INTEGER': 'int',
    'LONGVARBINARY': 'bin',
    'LONGVARCHAR': 'text',
    'NUMERIC': 'float',
    'REAL': 'float',
    'SMALLINT': 'int',
    'TIME': 'time',
    'TIMESTAMP': 'datetime',
    'TINYINT': 'int',
    'VARBINARY': 'bin',
    'VARCHAR': 'text',
    }

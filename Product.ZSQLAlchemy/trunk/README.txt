ZSQLAlchemy

(C) 2007, ZOPYX Ltd & Co. KG
D-72070 Tuebingen, Germany
www.zopyx.com, info@zopyx.com

Written by Andreas Jung

ZSQLAlchemy is published under the Zope Public License 2.1 (ZPL 2.1)



What is it:

    - ZSQLAlchemy tries to provide a basic SQLAlchemy infrastructure to be used
      with Zope applications. It basically acts like some kind of DA and cares
      automatically about connection and transaction handling


Limitations:

    - currently only supports Postgres through the psycopg2 Python bindings
      for Postgres

    - might not work properly from within untrusted code


Requirements:

    - Zope 2.8

    - sqlalchemy V 0.3.0 or higher

    - psycopg2 2.0.5


Basic usage:

    import sqlalchemy

    def test(self):

        zsqlalchemy = self.DA.getSession()   # 'DA' is ZSQLAlchemy instance
        session = zsqlalchemy.getSession()   # obtain a session proxy
        metadata = session.getMetaData()     # obtain metadata instance                                                                      

        # auto load 'users' table from postgres
        UsersTable = sqlalchemy.Table('users', metadata, autoload=True)

        # select some data
        s = UsersTable.select()
        for row in s.execute():
            print row

        # insert some data
        i = UsersTable.insert()
        i.execute(firstname='foo', lastname='bar')

        return 'done'

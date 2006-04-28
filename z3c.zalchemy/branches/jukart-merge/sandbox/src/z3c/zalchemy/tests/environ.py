import sqlalchemy

engine = sqlalchemy.ext.proxy.ProxyEngine()

testTable = sqlalchemy.Table(
        'testTable',
        engine,
        sqlalchemy.Column('id', sqlalchemy.Integer, primary_key = True),
        sqlalchemy.Column('x', sqlalchemy.Integer),
        )

illegalTable = sqlalchemy.Table(
        'illegalTable',
        sqlalchemy.create_engine('sqlite://'),
        sqlalchemy.Column('id', sqlalchemy.Integer, primary_key = True),
        )

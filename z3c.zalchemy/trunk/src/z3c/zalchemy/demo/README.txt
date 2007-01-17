ZAlchemy demos
==============

These demos show how ZAlchemy can be used to create Zope3 web applications that use SQLAlchemy to persist data in an RDBMS.

To try a demo, copy the included z3c.zalchemy.demo-configure.zcml file to your 
etc/package-includes/ directory and uncomment the demo you want to try.

Note: Do not try installing more than one of these demos at the same time. Due 
to a minor bug (hopefully soon eradicated), if ZAlchemy tries to create tables 
with the same name in different databases it produces an error (because of the
way the global MetaData() is used as an intermediary).

Because of incompatibilities between the database schemas, each demo defines a 
different database connection string, to avoid conflicts.

To try any particular demo, add a 'Message Container X' to a folder, where 'X'
is the number of the demo.  So for example, if you've uncommented demo_3 from
z3c.zalchemy.demo-configure.zcml, restarting Zope should show a 
'Message Container 3' object that can be added. Inside these message containers 
message objects can be added and edited. Adding a second 'Message Container' 
will show the same set of messages, as the container just gets all messages in 
the database.


Demo 1: Subclasses the included SQLAlchemyContainer to create a container that
        is preconfigured to hold only one class (HelloWordMessage)
        
Demo 2: Creates a container from scratch that is specialized to only hold one 
        class (HelloWorldMessage2).
        
Demo 3: Demonstrates a rudimentary adapter for storing Dublin Core metadata in 
        the RDBMS for HelloWorldMessage3 objects. HelloWorldMessage3 objects
        have editable title and description fields incorporated into the add and
        edit forms. The metadata is stored in a second table.
        
Demo 4: Demonstrates a contained HelloWorldMessage4 class that is in itself a
        container for HelloWorldFragment classes.
        

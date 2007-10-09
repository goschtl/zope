
===========
Grok Trails
===========

Cave men often hunted by following animal trails through the woods.
They could also follow trails to important natural resources;
the very first human migrations may have been along the trails
left by herds of migratory animals visiting natural salt deposits.

The Trails package allows you to define the URLs your users travel
in order to visit objects on your site, and also provides the means
by which Grok can determine what the URL for a given object should be.
Trails looks something like this when in use:

class MyTrails(megrok.trails.TrailHead):
    grok.context(MyApp)
    trails = [
        Trail('/person/:id', Person),
        Trail('/account/:username', Account),
        ]

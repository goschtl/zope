When an object cannot be correctly loaded from the ZODB, this package allows
this object still to be instantiated, but as a "Broken" object. This allows
for gracefully updating the database without interuption.

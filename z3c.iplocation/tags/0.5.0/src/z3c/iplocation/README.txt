==========
IP Locator
==========

The IP Locator is a utility that provides a location for a particular IP
address.

  >>> from z3c.iplocation import locator
  >>> loc = locator.IPLocator()

A location can be retrieved using:

  >>> loc.get('10.0.0.1')

If no location was found, as it is the case here, the default value which is
``None`` by default is returned. Of course, you can specify an alternative
default value:

  >>> loc.get('10.0.0.1', default=1)
  1

If the passed in value is not a valid IP address, an error is raised:

  >>> loc.get('10.0.0.x')
  Traceback (most recent call last):
  ...
  ValueError: invalid literal for int()...

An extension to the ip locator API is the ip location management, which allows
you to manage the locations within the utility. Let's now add a location.

  >>> us = locator.Location('24.225.0.0', '24.225.255.255', u'United States')
  >>> us
  <Location 24.225.0.0-24.225.255.255 u'United States'>

  >>> loc.add(us)

We can now locate IPs within this range:

  >>> loc.get('24.225.10.88')
  <Location 24.225.0.0-24.225.255.255 u'United States'>

Adding the same location again, is simply ignored:

  >>> loc.add(us)

Locations can as easily be removed:

  >>> loc.remove(us)

  >>> loc.get('24.225.10.88')

Deleting a non-existent location is silently ignored:

  >>> loc.remove(us)


IPligence Locations
-------------------

One of the providers for IP to location mappings is IPligence at
www.ipligence.com.


Lite Database
~~~~~~~~~~~~~

Let's load their demo version of the lite database:

  >>> import os
  >>> file = open(os.path.join(dirpath, 'ipligence-lite-demo.txt'), 'r')

  # Read some lines first
  >>> for count in xrange(5):
  ...     print file.readline().strip()
  ############ IPligence Lite DEMO FILE ###############
  (c) IPligence. All rights reserved.
  For more information visit http://www.ipligence.com
  #####################################################
  <BLANKLINE>

Let's now generate the locator:

  >>> from z3c.iplocation import ipligence
  >>> liteLocator = ipligence.createLocator(file, ipligence.LiteLocation)

We can now lookup locations:

  >>> loc = liteLocator.get('24.225.10.88')
  >>> loc
  <LiteLocation 24.225.0.0-24.225.255.255 u'UNITED STATES'>

  >>> loc.ipFrom
  '24.225.0.0'
  >>> loc.ipTo
  '24.225.255.255'
  >>> loc.name
  u'UNITED STATES'

  >>> loc.decimalFrom
  417398784
  >>> loc.decimalTo
  417464319
  >>> loc.countryCode
  'US'
  >>> loc.countryName
  'UNITED STATES'
  >>> loc.continentCode
  'NA'
  >>> loc.continentName
  'NORTH AMERICA'


Basic Database
~~~~~~~~~~~~~~

Let's load their demo version of the basic database:

  >>> import os
  >>> file = open(os.path.join(dirpath, 'ipligence-basic-demo.txt'), 'r')

  # Read some lines first
  >>> for count in xrange(5):
  ...     print file.readline().strip()
  ############ IPligence Basic DEMO FILE ###############
  (c) IPligence. All rights reserved.
  For more information visit http://www.ipligence.com
  #####################################################
  <BLANKLINE>

Let's now generate the locator:

  >>> from z3c.iplocation import ipligence
  >>> basicLocator = ipligence.createLocator(file, ipligence.BasicLocation)

We can now lookup locations:

  >>> loc = basicLocator.get('62.40.2.132')
  >>> loc
  <BasicLocation 62.40.2.40-62.40.2.255 u'GERMANY'>

  >>> loc.decimalFrom
  1042809384
  >>> loc.decimalTo
  1042809599
  >>> loc.countryCode
  'DE'
  >>> loc.countryName
  'GERMANY'
  >>> loc.continentCode
  'EU'
  >>> loc.continentName
  'EUROPE'
  >>> loc.owner
  'KLOECKNER-MOELLER GMBH'
  >>> loc.timeZone
  'GMT+1'
  >>> loc.regionCode
  'HE'
  >>> loc.regionName
  'HESSEN'


Max Database
~~~~~~~~~~~~

Let's load their demo version of the max database:

  >>> import os
  >>> file = open(os.path.join(dirpath, 'ipligence-max-demo.txt'), 'r')

  # Read some lines first
  >>> for count in xrange(5):
  ...     print file.readline().strip()
  ############ IPligence Max DEMO FILE ###############
  (c) IPligence. All rights reserved.
  For more information visit http://www.ipligence.com
  #####################################################
  <BLANKLINE>

Let's now generate the locator:

  >>> from z3c.iplocation import ipligence
  >>> maxLocator = ipligence.createLocator(file, ipligence.MaxLocation)

We can now lookup locations:

  >>> loc = maxLocator.get('62.21.101.13')
  >>> loc
  <MaxLocation 62.21.100.0-62.21.102.255 u'POLAND'>

  >>> loc.decimalFrom
  1041589248
  >>> loc.decimalTo
  1041590015
  >>> loc.countryCode
  'PL'
  >>> loc.countryName
  'POLAND'
  >>> loc.continentCode
  'EU'
  >>> loc.continentName
  'EUROPE'
  >>> loc.owner
  'INTERNET CABLE PROVIDER'
  >>> loc.timeZone
  'GMT+1'
  >>> loc.regionCode

  >>> loc.regionName

  >>> loc.cityName
  'WARSAW'
  >>> loc.countyName

  >>> loc.latitude
  52.25
  >>> loc.longitude
  21.0


update
------

An existing IPLocator can get updated with new data. If we do this, we will 
remove all existing data. Take care if you are using custom added data which
are not in the original ipligence data file.

Let's get the existing maxLocator and update them with the lite data file.

  >>> file = open(os.path.join(dirpath, 'ipligence-lite-demo.txt'), 'r')
  >>> maxLocator.update(file)
  Traceback (most recent call last):
  ...
  ValueError: Must use a ipligence location class.

As you can see, you must use a location class for update the data:

  >>> maxLocator.update(file, ipligence.MaxLocation)
  Traceback (most recent call last):
  ...
  ValueError: Wrong ipligence location class used or skipped the wrong amount of skipLines.

But you have to use the right ipligence location class:

  >>> file = open(os.path.join(dirpath, 'ipligence-lite-demo.txt'), 'r')
  >>> maxLocator.update(file, ipligence.LiteLocation)

Now we must get the lite location as result for the given IP:

  >>> liteLocator.get('24.225.10.88')
  <LiteLocation 24.225.0.0-24.225.255.255 u'UNITED STATES'>

Since we skip first 5 lines by default in the update method, let's check
the amount of locations which must be 42:

  >>> len(liteLocator._locations)
  42

reset
-----

The locator offers also a reset method which will remove all existing data and
can setup a clean empty locator. This method is used on initialization and 
before the data get updated like shown in the sample above. 

  >>> liteLocator.reset()

After the reset, the locator is empty and doesn't return any location:

  >>> liteLocator.get('24.225.10.88') is None
  True


Converting IPs to Decimals
--------------------------

In order to efficiently look up the location from the given IP, IPs are
converted to decimals.

  >>> from z3c.iplocation import locator

  >>> locator.getDecimal('123.29.4.1')
  2065499137
  >>> locator.getDecimal('0.0.0.0')
  0
  >>> locator.getDecimal('255.255.255.255')
  4294967295L


Converting Decimals to IPs
--------------------------

In order to provide a user-readable format of the IPs, the decimals can be
converted back to IP addresses:

  >>> locator.getIP(2065499137)
  '123.29.4.1'
  >>> locator.getIP(0)
  '0.0.0.0'
  >>> locator.getIP(4294967295L)
  '255.255.255.255'

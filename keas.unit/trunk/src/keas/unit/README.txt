==============
Unit Converter
==============

The unit converter is a simple utility to convert units. While it may seem to
be a trivial task initially, there are many different conventions and
combinations. Instead of inventing yet another unit conversion utility, this
package reuses the `units` shell command, which has the best implementation
that I have found out there.

  >>> from keas.unit import unit

The first step is to instantiate the unit converter object:

  >>> converter = unit.UnitConverter()

By default the converter uses the following path for the `units` command:

  >>> converter.executable
  '/usr/bin/units'

So let's make a simple unit conversion:

  >>> converter.convert('atm', 'kPa')
  Decimal("101.325")

There are several options that can be set on the conversion object. The first
one is the output format, which allows you to specify the precision on the
output. Of course, we then convert this output to a decimal:

  >>> converter.format
  >>> converter.format = '%.15g' # 15 decimal places
  >>> converter.convert('atm', 'kPa')
  Decimal("101.325")

Next you can specify additional unit conversion data filenames, so that custom
conversions can be loaded:

  >>> import os
  >>> datafile = os.path.join(
  ...     os.path.dirname(unit.__file__), 'test-conversions.dat')

  >>> converter.filenames
  >>> converter.filenames = ('', datafile)

  >>> converter.convert('keas', 'l')
  Decimal("0.54321")

  >>> converter.filenames = None

An empty name means that the default data file should be loaded as well.

The final option allows you to set whether the '-' character should be treated
as a multiplication operator, since it is used as such in some notations.

  >>> converter.minusAsProduct
  False
  >>> converter.minusAsProduct = True

  >>> converter.convert('m-m-m', 'l')
  Decimal("1000")

Finally, let's have a look at some error scenarios.

1. There is no known conversion from one unit to another:

  >>> converter.convert('kg', 'm')
  Traceback (most recent call last):
  ...
  UnitConversionError: ('/usr/bin/units -t -o %.15g -p "kg" "m"',
                        'conformability error')

2. One of the units is unknown:

  >>> converter.convert('kg', 'foo')
  Traceback (most recent call last):
  ...
  UnitConversionError: ('/usr/bin/units -t -o %.15g -p "kg" "foo"',
                        "Unknown unit 'foo'")

3. One of the units contains an invalid expression:

  >>> converter.convert('kg', 'm *')
  Traceback (most recent call last):
  ...
  UnitConversionError: ('/usr/bin/units -t -o %.15g -p "kg" "m *"',
                        "Error in 'm *': Parse error")

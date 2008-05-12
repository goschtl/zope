==========================
ISO 8601 utility functions
==========================

This package collects together functions supporting the data formats described
in ISO 8601.  Time zone support is provided by the ``pytz`` package.

The following functions are provided in the ``zc.iso8601.parse`` module:

``datetime(s)``
  Parse a date-time value that does not include time-zone information.
  Returns a Python datetime value.

``datetimetz(s)``
  Parse a date-time value that includes time-zone information.  Returns a
  Python datetime value in the UTC timezone.

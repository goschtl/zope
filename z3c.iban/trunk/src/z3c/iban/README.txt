==================
The Currency Field
==================

The IBAN field is a textual field, specifically designed to hold
the international bank account number (IBAN).

 >>> from z3c.iban import field, interfaces
 
 >>> iban1 = field.IBAN(
 ...     title=u'IBAN 1',
 ...     description=u'IBAN Number 1')

Now the field can be validated.

 >>> iban1.validate('UNKNOWNIBAN')      
 Traceback (most recent call last):
 ...
 ValidationError: Value is no valid IBAN

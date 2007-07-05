#!/usr/bin/env python
# -*-coding: utf-8 -*-

import unittest

def filterDigits(input):
    """" Strip the input of all non-digits, but retain last X if present. """
    input = input.strip()
    digits = [c for c in input if c.isdigit()]
    # an X may appear as check digit in ISBN-10
    if input[-1].upper() == 'X':
        digits.append('X')
    return ''.join(digits)

def checksumISBN10(digits):
    """ Return ISBN-10 check digit as a string of len 1 (may be 0-9 or X)
        References:
        http://www.isbn-international.org/en/userman/chapter4.html#usm4_4
        http://www.bisg.org/isbn-13/conversions.html
    """
    sum = 0
    for i, weight in enumerate(range(10,1,-1)):
        sum += int(digits[i]) * weight
    check = 11 - sum % 11
    if check == 10: return 'X'
    elif check == 11: return '0'
    return str(check)

def checksumEAN(digits):
    """ Return EAN check digit as a string (may be 0-9)
        Every ISBN-13 is a valid EAN
        Reference:
        http://www.bisg.org/isbn-13/conversions.html
    """
    sum = 0
    for i, d in enumerate(digits[:12]):
        weight = i%2*2+1
        sum += int(d) * weight
    check = 10 - sum % 10
    if check == 10: return '0'
    return str(check)

def validatedEAN(digits):
    if not digits:
        return None
    if len(digits) != 13:
        digits = filterDigits(digits)
        if len(digits) != 13:
            return None
    if digits[-1] == checksumEAN(digits):
        return digits

def validatedISBN10(digits):
    if not digits:
        return None
    if len(digits) != 10:
        digits = filterDigits(digits)
        if len(digits) != 10:
            return None
    if digits[-1] == checksumISBN10(digits):
        return digits

def validatedISBN13(digits):
    if not digits:
        return None
    if digits.strip()[:3] not in ['978','979']:
        return None
    return validatedEAN(digits)

def isValidISBN10(digits):
    return validatedISBN10(digits) is not None

def isValidISBN13(digits):
    return validatedISBN13(digits) is not None

def isValidEAN(digits):
    return validatedEAN(digits) is not None

def isValidISBN(digits):
    return isValidISBN10(digits) or isValidISBN13(digits)

def convertISBN10toISBN13(digits):
    digits = filterDigits(digits)
    if len(digits) != 10:
        raise ValueError, '%s is not a valid ISBN-10'
    else:
        return '978' + digits[:-1] + checksumEAN(digits)

# Note: ISBN group identifiers related to languages
# http://www.isbn-international.org/en/identifiers/allidentifiers.html
# http://www.loc.gov/standards/iso639-2/php/code_list.php
lang_groups = {
    'en':(0,1),'fr':(2,),'de':(3,),'jp':(4,), 'ru':(5,),
    'es':(84,           # Spain
          950, 987,     # Argentina
          956,          # Chile
          958,          # Colombia
          959,          # Cuba
          968, 970,     # Mexico
          980,          # Venezuela
          9942, 9978,   # Ecuador
          9945, 99934,  # Dominican Republic
          9962,         # Panama
          9968,         # Costa Rica (and 9977)	
          9972,         # Peru
          9974,         # Uruguay
          99922, 99939, # Guatemala
          99923,        # El Salvador
          99924,        # Nicaragua
          99925, 99953, # Paraguay 
          99926,        # Honduras
         ),
    'pt':(85,           # Brazil
          972, 989,     # Portugal
         ),
    }

group_lang = {}

for lang, groups in lang_groups.iteritems():
    for group in groups:
        group_lang[str(group)] = lang
        
def convertISBN13toLang(isbn13):
    assert len(isbn13)==13
    registration_group_field = isbn13[3:8]
    for i in range(1,6):
        possible_group = registration_group_field[:i]
        if possible_group in group_lang:
            return group_lang[possible_group]
    return None

class untitledTests(unittest.TestCase):
    def setUp(self):
        self.digits10ok0 = '0596002920'
        self.digits10ok2 = ' 853-521-714-2 '
        self.digits10ok9 = '0-3162-8929-9'
        self.digits10okX = '013147149X'
        self.digits10nok = '0131471490'
        self.digits13ok0 = '9780316289290'
        self.digits13ok8 = '9788535217148' # '978-85-352-1714-8'
        self.digits13nok = '9780596100679'
        self.digits13isbn = '9791231231233'

    def testFilterDigits(self):
        self.assertEquals('1234567890123',filterDigits('1234567890123'))
        self.assertEquals('0596101392',filterDigits('\t0 596 10139-2\n'))
        self.assertEquals('013147149X',filterDigits('0-13-147149-X'))
        self.assertEquals('1234X',filterDigits('X1X2X3X4X'))

    def testIsValidISBN10(self):
        self.assertTrue(isValidISBN10(self.digits10ok0))
        self.assertTrue(isValidISBN10(self.digits10ok2))
        self.assertTrue(isValidISBN10(self.digits10ok9))
        self.assertTrue(isValidISBN10(self.digits10okX))
        self.assertFalse(isValidISBN10(self.digits10nok))
        self.assertFalse(isValidISBN10(self.digits13ok0))

    def testIsValidEAN(self):
        self.assertTrue(isValidEAN(self.digits13ok0))
        self.assertTrue(isValidEAN(self.digits13ok8))
        self.assertFalse(isValidEAN(self.digits13nok))
        self.assertFalse(isValidEAN(self.digits10ok0))

    def testIsValidISBN13(self):
        self.assertTrue(isValidISBN13(self.digits13ok0))
        self.assertTrue(isValidISBN13(self.digits13ok8))
        self.assertFalse(isValidISBN13(self.digits13nok))
        self.assertFalse(isValidISBN13(self.digits10ok0))
        
    def testConvertISBN13toLang(self):
        self.assertEquals('en',convertISBN13toLang('0001234567890'))
        self.assertEquals('en',convertISBN13toLang('0000000000000'))
        self.assertEquals('fr',convertISBN13toLang('0002000000000'))
        self.assertEquals('pt',convertISBN13toLang('0008500000000')) # Brazil
        self.assertEquals('pt',convertISBN13toLang('0009720000000')) # Portugal
        self.assertEquals('pt',convertISBN13toLang('0009890000000')) # Portugal
        self.assertEquals('es',convertISBN13toLang('0008400000000')) # Spain
        self.assertEquals('es',convertISBN13toLang('0009992500000')) # Paraguay
        self.assertEquals('es',convertISBN13toLang('0009995300000')) # Paraguay


if __name__ == '__main__':
    unittest.main()

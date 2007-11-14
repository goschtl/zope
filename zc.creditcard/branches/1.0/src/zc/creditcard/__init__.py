"""Utilities for credit card processing

$Id$
"""

# Constants for the supported card types

AMEX = 'AMEX'
DISCOVER = 'Discover'
MASTERCARD = 'MasterCard'
VISA = 'Visa'
UNKNOWN_CARD_TYPE = 'Unknown'


def identifyCreditCardType(card_num, card_len):
    """ Identifies the credit card type based on information on the
    following site(s):

    http://en.wikipedia.org/wiki/Credit_card_number
    http://www.beachnet.com/~hstiles/cardtype.html

    This checks the prefix (first 4 digits) and the length of the card number to
    identify the type of the card. This method is used because Authorize.net
    does not provide this information. This method currently identifies only
    the following four types:

    1. VISA
    2. MASTERCARD
    3. Discover
    4. AMEX

    Before we test, lets create a few dummy credit-card numbers:

        >>> amex_card_num = '370000000000002'
        >>> disc_card_num = '6011000000000012'
        >>> mc_card_num = '5424000000000015'
        >>> visa_card_num = '4007000000027'
        >>> unknown_card_num = '400700000002'

        >>> identifyCreditCardType(amex_card_num, len(amex_card_num)) == AMEX
        True

        >>> identifyCreditCardType(disc_card_num,
        ...                        len(disc_card_num)) == DISCOVER
        True

        >>> identifyCreditCardType(mc_card_num, len(mc_card_num)) == MASTERCARD
        True

        >>> identifyCreditCardType(visa_card_num, len(visa_card_num)) == VISA
        True

        >>> identifyCreditCardType(unknown_card_num,
        ...                        len(unknown_card_num)) == UNKNOWN_CARD_TYPE
        True

    """
    card_type = UNKNOWN_CARD_TYPE
    card_1_digit = card_num[0]
    card_2_digits = card_num[:2]
    card_4_digits = card_num[:4]

    # AMEX
    if (card_len == 15) and card_2_digits in ('34', '37'):
        card_type = AMEX

    # MASTERCARD, DISCOVER & VISA
    elif card_len == 16:
        # MASTERCARD
        if card_2_digits in ('51', '52', '53', '54', '55'):
            card_type = MASTERCARD

        # DISCOVER
        elif (card_4_digits == '6011') or (card_2_digits == '65'):
            card_type = DISCOVER

        # VISA
        elif (card_1_digit == '4'):
            card_type = VISA

    # VISA
    elif (card_len == 13) and (card_1_digit == '4'):
        card_type = VISA

    return card_type

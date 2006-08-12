# Make a package

import zope.i18nmessageid
_ = zope.i18nmessageid.MessageFactory('rating')

from manager import getRatingsManager
from definition import RatingDefinition
from rating import Rating

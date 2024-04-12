import re
from datetime import datetime

from django.core.exceptions import ValidationError

from api_yamdb.settings import RESERVED_USERNAMES

YEAR_ERROR = 'Invalid year: "{year}". Value should be <= "{current_year}".'
USERNAME_ERROR = 'Username "{username}" is not allowed.'
PATTERN = r'[^\w.@+-]+'
USERNAME_FORBIDDEN_SYMBOLS = (
    '"{symbols}" is not allowed in username. '
    'Please use only letters, digits or ".@+-"'
)


def year_validator(value):
    current_year = datetime.now().year
    if value > current_year:
        raise ValidationError(YEAR_ERROR.format(
            year=value,
            current_year=current_year
        ))
    return value


def username_validator(value):
    if value in RESERVED_USERNAMES:
        raise ValidationError(USERNAME_ERROR.format(username=value))
    forbidden_symbols = ''.join(set(re.findall(PATTERN, value)))
    if forbidden_symbols:
        raise ValidationError(
            USERNAME_FORBIDDEN_SYMBOLS.format(symbols=forbidden_symbols)
        )
    return value

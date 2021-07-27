import datetime

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def year_validator(value):
    if value < 1900 or value > datetime.datetime.now().year:
        raise ValidationError(
            _('%(value)s is not a correct year!'),
            params={'value': value},
        )

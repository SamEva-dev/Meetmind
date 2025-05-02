import pytz
import os

from datetime import datetime

def ensure_utc_aware(dt: datetime) -> datetime:
    """
    Si dt.n’a pas de tzinfo, on le localise en UTC.
    Sinon, on le convertit en UTC.
    """
    if dt.tzinfo is None:
        return pytz.utc.localize(dt)
    else:
        return dt.astimezone(pytz.utc)

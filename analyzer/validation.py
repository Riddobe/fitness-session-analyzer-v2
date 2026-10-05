import re

# regex patterns for the identifiers used in this assignment
PARTICIPANT_ID_PATTERN = re.compile(r"^P\d{3}$")
SESSION_ID_PATTERN = re.compile(r"^FIT-\d{4}-\d{3}$")

# valid ranges for each measurement field
FIELD_LIMITS = {
    "heart_rate": (35, 205),
    "skin_response": (0, 1000),
    "temperature": (25, 42),
    "activity_level": (0, 1),
    "signal_quality": (0, 1),
}

# every field a session row must have
REQUIRED_SESSION_FIELDS = [
    "session_id",
    "participant_id",
    "timestamp",
    "heart_rate",
    "skin_response",
    "temperature",
    "activity_level",
    "signal_quality",
]

# readings below this quality are treated as a data-quality problem
MIN_SIGNAL_QUALITY = 0.60


class InvalidIdentifierError(ValueError):
    """Raised when an identifier has an invalid format."""


class InvalidRecordError(ValueError):
    """Raised when a CSV record cannot be accepted."""


def validate_participant_id(value):
    # checks the participant id format, for example P001
    if not PARTICIPANT_ID_PATTERN.fullmatch(value):
        raise InvalidIdentifierError(f"participant id '{value}' must look like P001")
    return value


def validate_session_id(value):
    # checks the session id format, for example FIT-2026-001
    if not SESSION_ID_PATTERN.fullmatch(value):
        raise InvalidIdentifierError(f"session id '{value}' must look like FIT-2026-001")
    return value


def check_row_length(row):
    # checks that a session row has exactly the fields we expect
    if None in row:
        # DictReader puts extra columns under the key None
        raise InvalidRecordError("row has more fields than expected")
    for field in REQUIRED_SESSION_FIELDS:
        if row.get(field) is None:
            raise InvalidRecordError(f"row is missing the field '{field}'")
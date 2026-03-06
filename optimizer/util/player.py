import re

_SUFFIX_PATTERN = re.compile(r'\b(jr\.?|sr\.?|ii|iii|iv)\b', re.IGNORECASE)
_NON_ALPHA = re.compile(r'[^a-z]')


def generate_player_id(first_name: str, last_name: str, team: str) -> str:
    """Generate a consistent player ID from name and team.

    Format: first3chars_lastname_team (all lowercase, alpha only).
    Suffixes like 'Jr.', 'Sr.', 'II', 'III', 'IV' are stripped from last name.
    """
    cleaned_last = _SUFFIX_PATTERN.sub('', last_name).strip()

    first_part = _NON_ALPHA.sub('', first_name.lower())[:3]
    last_part = _NON_ALPHA.sub('', cleaned_last.lower())
    team_part = _NON_ALPHA.sub('', team.lower())

    return f"{first_part}_{last_part}_{team_part}"

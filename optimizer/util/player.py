import re


def generate_player_id(first_name: str, last_name: str, team: str) -> str:
    """Generate a consistent player ID from name and team.

    Format: first3chars_lastname_team (all lowercase, alpha only).
    Suffixes like 'Jr.', 'Sr.', 'II', 'III', 'IV' are stripped from last name.
    """
    suffixes = re.compile(r'\b(jr\.?|sr\.?|ii|iii|iv)\b', re.IGNORECASE)
    cleaned_last = suffixes.sub('', last_name).strip()

    first_part = re.sub(r'[^a-z]', '', first_name.lower())[:3]
    last_part = re.sub(r'[^a-z]', '', cleaned_last.lower())
    team_part = re.sub(r'[^a-z]', '', team.lower())

    return f"{first_part}_{last_part}_{team_part}"

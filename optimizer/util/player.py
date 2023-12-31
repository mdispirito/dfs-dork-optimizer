
def generate_player_id(first_name, last_name, team):
    # TODO - really janky, do this properly
    # TODO - check if team is valid and use it in ID
    stripped_last_name = last_name.lower().replace("jr.", "")

    converted_first_name = "".join([char for char in first_name if char.isalpha()])[:3]
    converted_last_name = "".join([char for char in stripped_last_name if char.isalpha()])
    id = converted_first_name.lower() + "_" + converted_last_name.lower()

    return id

from optimizer.util.player import generate_player_id


class TestGeneratePlayerId:

    def test_basic(self):
        assert generate_player_id("LeBron", "James", "LAL") == "leb_james_lal"

    def test_truncates_first_name_to_three_chars(self):
        assert generate_player_id("Stephen", "Curry", "GSW") == "ste_curry_gsw"

    def test_strips_jr_suffix(self):
        assert generate_player_id("Jaren", "Jackson Jr.", "MEM") == "jar_jackson_mem"

    def test_strips_sr_suffix(self):
        assert generate_player_id("John", "Smith Sr.", "BOS") == "joh_smith_bos"

    def test_strips_roman_numeral_ii(self):
        assert generate_player_id("John", "Wall II", "HOU") == "joh_wall_hou"

    def test_strips_roman_numeral_iii(self):
        assert generate_player_id("John", "Smith III", "LAC") == "joh_smith_lac"

    def test_strips_roman_numeral_iv(self):
        assert generate_player_id("John", "Smith IV", "NYK") == "joh_smith_nyk"

    def test_case_insensitive(self):
        assert generate_player_id("LEBRON", "JAMES", "lal") == "leb_james_lal"

    def test_removes_non_alpha_characters(self):
        assert generate_player_id("De'Aaron", "Fox", "SAC") == "dea_fox_sac"

    def test_short_first_name(self):
        assert generate_player_id("Al", "Horford", "BOS") == "al_horford_bos"

from helga_koji.actions.user_tasks import TaskMatch


class TestTaskMatch(object):
    def test_simple(self):
        match = TaskMatch.from_text("kdreyer")
        assert match.user == 'kdreyer'
        assert match.state == 'open'

    def test_possessive_username(self):
        match = TaskMatch.from_text("kdreyer's")
        assert match.user == 'kdreyer'
        assert match.state == 'open'

    def test_state(self):
        match = TaskMatch.from_text("kdreyer's failed")
        assert match.user == 'kdreyer'
        assert match.state == 'failed'

    def test_possessive_username_with_s(self):
        match = TaskMatch.from_text("ahills'")
        assert match.user == 'ahills'
        assert match.state == 'open'

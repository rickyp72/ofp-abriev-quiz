import pytest
from app import app
from data import QUESTIONS

VALID_CATS = {"wx", "fuel", "nav", "atc", "perf", "airspace"}


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# Data integrity
# ---------------------------------------------------------------------------

class TestData:
    def test_questions_not_empty(self):
        assert len(QUESTIONS) > 0

    def test_each_question_has_four_fields(self):
        for q in QUESTIONS:
            assert len(q) == 4, f"{q[0]!r} does not have 4 fields"

    def test_abbreviations_are_non_empty_strings(self):
        for abbr, *_ in QUESTIONS:
            assert isinstance(abbr, str) and abbr.strip(), f"Invalid abbr: {abbr!r}"

    def test_categories_are_valid(self):
        for abbr, cat, *_ in QUESTIONS:
            assert cat in VALID_CATS, f"{abbr!r} has unknown category: {cat!r}"

    def test_correct_answers_are_non_empty_strings(self):
        for abbr, _, correct, _ in QUESTIONS:
            assert isinstance(correct, str) and correct.strip(), f"{abbr!r} has empty correct answer"

    def test_each_question_has_three_wrong_answers(self):
        for abbr, _, _, wrongs in QUESTIONS:
            assert len(wrongs) == 3, f"{abbr!r} has {len(wrongs)} wrong answers, expected 3"

    def test_wrong_answers_are_non_empty_strings(self):
        for abbr, _, _, wrongs in QUESTIONS:
            for w in wrongs:
                assert isinstance(w, str) and w.strip(), f"{abbr!r} has empty wrong answer"

    def test_no_duplicate_abbreviations(self):
        abbrs = [q[0] for q in QUESTIONS]
        dupes = {a for a in abbrs if abbrs.count(a) > 1}
        assert not dupes, f"Duplicate abbreviations: {dupes}"

    def test_correct_answer_not_among_wrongs(self):
        for abbr, _, correct, wrongs in QUESTIONS:
            assert correct not in wrongs, f"{abbr!r}: correct answer appears in wrong answers list"

    def test_all_options_are_distinct(self):
        for abbr, _, correct, wrongs in QUESTIONS:
            all_opts = [correct] + list(wrongs)
            assert len(all_opts) == len(set(all_opts)), f"{abbr!r} has duplicate option text"


# ---------------------------------------------------------------------------
# Flask routes
# ---------------------------------------------------------------------------

class TestRoutes:
    def test_home_returns_200(self, client):
        assert client.get("/").status_code == 200

    def test_home_contains_title(self, client):
        assert b"FlightSimBridge" in client.get("/").data

    def test_home_contains_quiz_link(self, client):
        assert b'href="/quiz"' in client.get("/").data

    def test_quiz_returns_200(self, client):
        assert client.get("/quiz").status_code == 200

    def test_quiz_contains_title(self, client):
        assert b"OFP Abbreviation Quiz" in client.get("/quiz").data

    def test_api_questions_returns_200(self, client):
        assert client.get("/api/questions").status_code == 200

    def test_api_questions_content_type_is_json(self, client):
        res = client.get("/api/questions")
        assert "application/json" in res.content_type

    def test_api_returns_ten_questions(self, client):
        data = client.get("/api/questions").get_json()
        assert len(data) == min(10, len(QUESTIONS))

    def test_api_question_has_required_fields(self, client):
        for q in client.get("/api/questions").get_json():
            assert {"abbr", "cat", "correct", "options"} <= q.keys()

    def test_api_each_question_has_four_options(self, client):
        for q in client.get("/api/questions").get_json():
            assert len(q["options"]) == 4, f"{q['abbr']!r} does not have 4 options"

    def test_api_correct_always_in_options(self, client):
        for q in client.get("/api/questions").get_json():
            assert q["correct"] in q["options"], f"{q['abbr']!r}: correct answer missing from options"

    def test_api_categories_are_valid(self, client):
        for q in client.get("/api/questions").get_json():
            assert q["cat"] in VALID_CATS, f"{q['abbr']!r} has invalid category: {q['cat']!r}"

    def test_api_no_duplicate_questions_in_one_round(self, client):
        abbrs = [q["abbr"] for q in client.get("/api/questions").get_json()]
        assert len(abbrs) == len(set(abbrs)), "Duplicate questions returned in one round"

    def test_api_category_filter_returns_correct_category(self, client):
        for cat in ["wx", "nav", "atc", "fuel", "perf", "airspace"]:
            data = client.get(f"/api/questions?cat={cat}").get_json()
            assert all(q["cat"] == cat for q in data), f"Non-{cat} question returned when filtering by {cat}"

    def test_api_category_filter_unknown_returns_empty(self, client):
        data = client.get("/api/questions?cat=unknown").get_json()
        assert data == []

    def test_api_no_filter_returns_mixed_categories(self, client):
        cats = {q["cat"] for q in client.get("/api/questions").get_json()}
        assert len(cats) > 1, "Unfiltered quiz should return multiple categories"

    def test_api_randomises_question_selection(self, client):
        orders = {tuple(q["abbr"] for q in client.get("/api/questions").get_json()) for _ in range(8)}
        assert len(orders) > 1, "Question order was identical across 8 calls — randomisation may be broken"

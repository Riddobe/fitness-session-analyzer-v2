import unittest

from analyzer.validation import (
    InvalidIdentifierError,
    InvalidRecordError,
    validate_participant_id,
    validate_session_id,
    check_row_length,
)
from analyzer.models import ReferenceProfile, Participant, Session
from analyzer.loader import load_participants, load_sessions, validate_observation_row
from analyzer.analysis import SessionClassifier, analyze_session, check_recovery

GOOD_ROW = {
    "session_id": "FIT-2026-001",
    "participant_id": "P001",
    "timestamp": "0",
    "heart_rate": "100",
    "skin_response": "2.0",
    "temperature": "32.5",
    "activity_level": "0.5",
    "signal_quality": "0.9",
}


class TestRegexValidation(unittest.TestCase):
    def test_valid_participant_id(self):
        self.assertEqual(validate_participant_id("P001"), "P001")

    def test_invalid_participant_id_raises_error(self):
        with self.assertRaises(InvalidIdentifierError):
            validate_participant_id("001")

    def test_valid_session_id(self):
        self.assertEqual(validate_session_id("FIT-2026-001"), "FIT-2026-001")

    def test_invalid_session_id_raises_error(self):
        with self.assertRaises(InvalidIdentifierError):
            validate_session_id("FIT-26-102")


class TestRowLength(unittest.TestCase):
    def test_complete_row_passes(self):
        check_row_length(GOOD_ROW)  # should not raise

    def test_missing_field_raises_error(self):
        bad_row = dict(GOOD_ROW)
        del bad_row["signal_quality"]
        with self.assertRaises(InvalidRecordError):
            check_row_length(bad_row)


class TestObservationValidation(unittest.TestCase):
    def test_valid_row_has_no_problems(self):
        self.assertEqual(validate_observation_row(GOOD_ROW), [])

    def test_impossible_value_is_flagged(self):
        bad_row = dict(GOOD_ROW)
        bad_row["heart_rate"] = "300"
        self.assertTrue(validate_observation_row(bad_row))

    def test_non_numeric_value_is_flagged(self):
        bad_row = dict(GOOD_ROW)
        bad_row["heart_rate"] = "fast"
        self.assertTrue(validate_observation_row(bad_row))

    def test_boundary_values_are_accepted(self):
        edge_row = dict(GOOD_ROW)
        edge_row["heart_rate"] = "35"  # exact lower boundary
        edge_row["activity_level"] = "1"  # exact upper boundary
        self.assertEqual(validate_observation_row(edge_row), [])


class TestFileLoading(unittest.TestCase):
    def test_missing_participants_file_raises_error(self):
        with self.assertRaises(FileNotFoundError):
            load_participants("data/does_not_exist.csv")

    def test_missing_sessions_file_raises_error(self):
        with self.assertRaises(FileNotFoundError):
            load_sessions("data/does_not_exist.csv", {})

    def test_real_participants_file_loads(self):
        participants = load_participants("data/participants.csv")
        self.assertIn("P001", participants)

    def test_invalid_sessions_file_rejects_bad_rows(self):
        participants = load_participants("data/participants.csv")
        sessions, rejected = load_sessions("data/fitness_sessions_invalid.csv", participants)
        self.assertGreater(len(rejected), 0)


class TestClassification(unittest.TestCase):
    def test_resting_session(self):
        participant = Participant("P1", "Test Person", ReferenceProfile(70))
        obs = [dict(heart_rate=72, activity_level=0.1) for _ in range(6)]
        session = Session("FIT-2026-999", participant, obs)
        result = analyze_session(session, SessionClassifier())
        self.assertEqual(result["classification"], "resting")

    def test_insufficient_data(self):
        participant = Participant("P1", "Test Person", ReferenceProfile(70))
        session = Session("FIT-2026-999", participant, [{"heart_rate": 70, "activity_level": 0.1}])
        result = analyze_session(session, SessionClassifier())
        self.assertEqual(result["classification"], "insufficient_data")

    def test_recovery_detected(self):
        heart_rates = [130, 125, 120, 100, 85, 78, 75, 74, 73]
        activities = [0.8, 0.8, 0.7, 0.5, 0.3, 0.2, 0.1, 0.1, 0.1]
        obs = []
        for hr, act in zip(heart_rates, activities):
            obs.append({"heart_rate": hr, "activity_level": act})
        self.assertTrue(check_recovery(obs, 70))


if __name__ == "__main__":
    unittest.main()
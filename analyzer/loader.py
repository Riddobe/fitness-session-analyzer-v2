import csv
from pathlib import Path

from analyzer.models import Participant, ReferenceProfile, Session
from analyzer.validation import (
    FIELD_LIMITS,
    InvalidIdentifierError,
    InvalidRecordError,
    check_row_length,
    validate_participant_id,
    validate_session_id,
)


def load_participants(path):
    # reads participants.csv and returns a dict of participant_id -> Participant
    participants = {}
    try:
        with open(path, "r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    participant_id = validate_participant_id(row["participant_id"])
                    heart_rate = float(row["baseline_heart_rate"])
                    reference = ReferenceProfile(heart_rate)
                    participant = Participant(participant_id, row["name"], reference)
                    participants[participant_id] = participant
                except (InvalidIdentifierError, ValueError, KeyError) as error:
                    print(f"Skipped a participant row: {error}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find participants file: {path}")
    return participants


def validate_observation_row(row):
    # checks one session row, returns a list of problems (empty = ok)
    problems = []

    timestamp_value = row.get("timestamp")
    try:
        timestamp_number = int(timestamp_value)
        if timestamp_number < 0:
            problems.append("timestamp is negative")
    except (ValueError, TypeError):
        problems.append("timestamp is not a whole number")

    for field, (low, high) in FIELD_LIMITS.items():
        value = row.get(field)
        if value is None or value == "":
            problems.append(f"{field} is missing")
            continue
        try:
            number = float(value)
        except ValueError:
            problems.append(f"{field} is not a number")
            continue
        if number < low or number > high:
            problems.append(f"{field} is out of range")
    return problems


def load_sessions(path, participants):
    # reads a sessions CSV file and groups rows into Session objects
    # returns (sessions_dict, rejected_rows_list)
    sessions = {}
    rejected = []

    try:
        with open(path, "r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            for row_number, row in enumerate(reader, start=2):
                try:
                    check_row_length(row)
                except InvalidRecordError as error:
                    rejected.append({
                        "file": str(path),
                        "row": row_number,
                        "field": "row_length",
                        "reason": str(error),
                    })
                    continue

                try:
                    session_id = validate_session_id(row["session_id"])
                except InvalidIdentifierError as error:
                    rejected.append({
                        "file": str(path),
                        "row": row_number,
                        "field": "session_id",
                        "reason": str(error),
                    })
                    continue

                participant_id = row.get("participant_id")
                if participant_id not in participants:
                    rejected.append({
                        "file": str(path),
                        "row": row_number,
                        "field": "participant_id",
                        "reason": f"unknown participant '{participant_id}'",
                    })
                    continue

                problems = validate_observation_row(row)
                if problems:
                    for problem in problems:
                        rejected.append({
                            "file": str(path),
                            "row": row_number,
                            "field": "observation",
                            "reason": problem,
                        })
                    continue

                observation = {
                    "timestamp": int(row["timestamp"]),
                    "heart_rate": float(row["heart_rate"]),
                    "skin_response": float(row["skin_response"]),
                    "temperature": float(row["temperature"]),
                    "activity_level": float(row["activity_level"]),
                    "signal_quality": float(row["signal_quality"]),
                }

                if session_id not in sessions:
                    sessions[session_id] = Session(session_id, participants[participant_id], [])
                sessions[session_id].observations.append(observation)
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find sessions file: {path}")

    return sessions, rejected
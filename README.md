# Smart Fitness Session Analyzer V2

Option A: Smart Fitness Session Analyzer

Student name: Ridouan Boulahyane Essaeh

Student number: riess0465

## Description

This program reads fitness session data from CSV files. It checks that participant and session ids follow the right format using regular expressions, checks every reading for missing,
impossible or badly typed values, and reports exactly which file, row,
field and reason caused a record to be rejected. It then compares the
good data with each participant's normal heart rate and decides if the
session was resting, moderate activity, high activity, recovering, or
insufficient data. The results are saved as report files in an output
folder.

## How to run it

```bash
git clone https://github.com/Riddobe/fitness-session-analyzer-v2.git
cd fitness-session-analyzer-v2
python3 main.py --profiles data/participants.csv --sessions data/fitness_sessions.csv --output output
```

To see what happens with bad data:

```bash
python3 main.py --profiles data/participants.csv --sessions data/fitness_sessions_invalid.csv --output output
```

To run the tests:

```bash
python3 tests.py
```

## Files

| File / folder | What it contains |
|---|---|
| `main.py` | Reads command line arguments and runs the whole program |
| `analyzer/models.py` | The classes: ReferenceProfile, Participant, Session |
| `analyzer/validation.py` | Regex patterns, the custom exceptions, and row-length checks |
| `analyzer/loader.py` | Reads the CSV files and builds the objects |
| `analyzer/analysis.py` | The classification logic |
| `analyzer/reports.py` | Writes the three output files |
| `data/` | The CSV files given for the assignment |
| `output/` | Created automatically, holds the report files |
| `tests.py` | Unit tests |
| `requirements.txt` | Says the project only uses the standard library |

## Class design

ReferenceProfile stores a participant's normal heart rate. The value is
private and can only be set through a property, which checks that it is
realistic.

Participant has an id, a name, and a ReferenceProfile. This is
composition, since a Participant "has" a ReferenceProfile.

Session has a session id, a Participant, and a list of readings. This is
also composition.

IntensityClassifier is a base class that decides resting/moderate/high
from heart rate above the baseline.

SessionClassifier inherits from IntensityClassifier and overrides
classify() to add the insufficient-data and recovery checks first, then
falls back to the base class for normal intensity.

## Custom exceptions

InvalidIdentifierError is raised when a participant id or session id does
not match the required format (checked with regex). It is caught in
loader.py, where the row is added to the rejected list instead of
crashing the program.

InvalidRecordError is raised when a row has a missing field or an
unexpected number of columns. It is also caught in loader.py for the same
reason.

## Regular expressions used

Participant id must match `^P\d{3}$` (P followed by three digits).

Session id must match `^FIT-\d{4}-\d{3}$` (FIT, a four digit year, and a
three digit number).

## Error handling

The program uses targeted try/except blocks instead of one broad
except. FileNotFoundError is caught separately when a CSV file cannot be
found. ValueError and KeyError are caught separately when a participant
row cannot be converted to the right types. InvalidIdentifierError and
InvalidRecordError are caught separately so that a single bad row does
not stop the rest of the file from being processed.

## Assumptions and classification rules

A reading is rejected if the row is missing a field, a value is not a
number, or a value is outside its normal range (heart rate 35-205, skin
response 0 to 1000, temperature 25-42, activity level 0-1, signal
quality 0-1). A row is also rejected if its participant id does not
exist in participants.csv, or if its session id does not match the
required format.

The session is classified using these rules, checked in this order:

1. Insufficient data: fewer than 4 usable readings.
2. Recovering: heart rate starts at least 20 bpm above baseline, then
   drops by at least 15 bpm, and activity drops by at least 0.20,
   comparing the first third of the session with the last third.
3. High activity: average heart rate is at least 45 bpm above baseline.
4. Moderate activity: average heart rate is at least 15 bpm above
   baseline.
5. Resting: none of the above.

## Output files

Running the program creates an output folder with three files:

analysis_summary.csv has one row per accepted session, with the
classification and a short explanation.

analysis_report.txt has a readable paragraph for each session.

rejected_records.txt lists every rejected row with the file name, row
number, field and reason.

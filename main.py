import argparse

from analyzer.loader import load_participants, load_sessions
from analyzer.analysis import analyze_session, SessionClassifier
from analyzer.reports import (
    ensure_output_dir,
    write_summary_csv,
    write_analysis_report,
    write_rejected_records,
)


def parse_arguments():
    # reads the command line options
    parser = argparse.ArgumentParser(description="Smart Fitness Session Analyzer")
    parser.add_argument("--profiles", required=True, help="path to participants.csv")
    parser.add_argument("--sessions", required=True, help="path to the sessions csv file")
    parser.add_argument("--output", required=True, help="folder to save the reports in")
    return parser.parse_args()


def main():
    args = parse_arguments()

    try:
        participants = load_participants(args.profiles)
    except FileNotFoundError as error:
        print(f"Error: {error}")
        return

    try:
        sessions, rejected = load_sessions(args.sessions, participants)
    except FileNotFoundError as error:
        print(f"Error: {error}")
        return

    classifier = SessionClassifier()
    results = []
    for session in sessions.values():
        result = analyze_session(session, classifier)
        results.append(result)

    ensure_output_dir(args.output)
    write_summary_csv(results, args.output)
    write_analysis_report(results, args.output)
    write_rejected_records(rejected, args.output)

    print(f"Accepted sessions: {len(results)}")
    print(f"Rejected rows: {len(rejected)}")
    print(f"Reports saved to: {args.output}")


if __name__ == "__main__":
    main()
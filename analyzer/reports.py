import csv
from pathlib import Path


def ensure_output_dir(output_path):
    # creates the output directory if it does not already exist
    path = Path(output_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_summary_csv(results, output_path):
    # writes one row per session to analysis_summary.csv
    file_path = Path(output_path) / "analysis_summary.csv"
    with open(file_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "session_id", "participant_id", "participant_name",
            "classification", "observation_count", "explanation",
        ])
        for result in results:
            writer.writerow([
                result["session_id"],
                result["participant_id"],
                result["participant_name"],
                result["classification"],
                result["observation_count"],
                result["explanation"],
            ])
    return file_path


def write_analysis_report(results, output_path):
    # writes a readable explanation for each session to analysis_report.txt
    file_path = Path(output_path) / "analysis_report.txt"
    with open(file_path, "w", encoding="utf-8") as file:
        for result in results:
            file.write("=" * 50 + "\n")
            file.write(f"Session: {result['session_id']}   ")
            file.write(f"Participant: {result['participant_name']} ({result['participant_id']})\n")
            file.write(f"Classification: {result['classification'].upper()}\n")
            file.write(f"Usable observations: {result['observation_count']}\n")
            file.write(f"Why: {result['explanation']}\n")
            file.write("\n")
    return file_path


def write_rejected_records(rejected, output_path):
    # writes every rejected row with the reason to rejected_records.txt
    file_path = Path(output_path) / "rejected_records.txt"
    with open(file_path, "w", encoding="utf-8") as file:
        if not rejected:
            file.write("No rejected records.\n")
        for item in rejected:
            file.write(
                f"File: {item['file']}  Row: {item['row']}  "
                f"Field: {item['field']}  Reason: {item['reason']}\n"
            )
    return file_path
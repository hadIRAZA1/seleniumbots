import json
import os

LOG_FILE = "automation_logs.jsonl"

def view_automation_logs():
    if not os.path.exists(LOG_FILE):
        print(f"Error: Log file '{LOG_FILE}' not found in the current directory.")
        return

    print(f"--- Contents of {LOG_FILE} ---")
    print("-" * (len(LOG_FILE) + 20))

    try:
        with open(LOG_FILE, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    log_entry = json.loads(line)
                    print(f"\nLog Entry {line_num}:")
                    print(json.dumps(log_entry, indent=4)) # Pretty print the JSON
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON on line {line_num}: {e}")
                    print(f"Problematic line: {line.strip()}")
    except Exception as e:
        print(f"An error occurred while reading the log file: {e}")

if __name__ == "__main__":
    view_automation_logs()
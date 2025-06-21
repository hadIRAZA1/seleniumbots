import streamlit as st
import subprocess
import os
import json
import time
import sys
import pandas as pd # Import pandas for DataFrame

# --- MODIFIED: Use an absolute path relative to the script's location ---
# Get the absolute path of the directory where this script (app.py) is located
APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the log directory path relative to the app's directory
LOG_DIR = os.path.join(APP_DIR, "logs")

# Define the full log file path
LOG_FILE_PATH = os.path.join(LOG_DIR, "automation_logs.jsonl")

# Create the log directory if it doesn't exist
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR, exist_ok=True)
# --- END MODIFIED ---

def run_script(script_name, log_placeholder=None):
    """
    Runs a Python script as a subprocess and captures its output.
    This function *requires* the Streamlit app to be running on the same machine
    as the Selenium scripts.
    Returns True on success, False on failure.
    """
    st.info(f"Running {script_name}...")
    
    if script_name == "sel.py" and st.session_state.get('clear_console_on_next_sequence', True):
        st.session_state['stdout'] = []
        st.session_state['stderr'] = []
        st.session_state['clear_console_on_next_sequence'] = False

    current_output_placeholder = log_placeholder if log_placeholder else st.empty()
    
    try:
        # The script_dir is now the same as APP_DIR, ensuring consistency.
        script_dir = APP_DIR 
        
        process = subprocess.Popen(
            [sys.executable, "-u", os.path.join(script_dir, script_name)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            cwd=script_dir
        )

        full_stdout = []
        full_stderr = []

        while process.poll() is None:
            output = process.stdout.readline()
            if output:
                full_stdout.append(output.strip())
                with current_output_placeholder.container():
                    st.code("\n".join(full_stdout))

            error_output = process.stderr.readline()
            if error_output:
                full_stderr.append(error_output.strip())
                with current_output_placeholder.container():
                    st.error("ERROR:\n" + "\n".join(full_stderr))
            
            time.sleep(0.1)

        remaining_stdout, remaining_stderr = process.communicate()
        if remaining_stdout:
            full_stdout.extend(remaining_stdout.strip().split('\n'))
        if remaining_stderr:
            full_stderr.extend(remaining_stderr.strip().split('\n'))

        with current_output_placeholder.container():
            st.code("\n".join(full_stdout))
            if full_stderr:
                st.error("ERROR:\n" + "\n".join(full_stderr))

        st.session_state['stdout'].extend(full_stdout)
        st.session_state['stderr'].extend(full_stderr)

        if process.returncode == 0:
            st.success(f"Successfully ran {script_name}")
            return True
        else:
            st.error(f"Error running {script_name}. Exit code: {process.returncode}")
            return False

    except FileNotFoundError:
        st.error(f"Error: Python or the script '{script_name}' was not found. Make sure Python is in your PATH and the script exists at '{os.path.join(script_dir, script_name)}'.")
        return False
    except Exception as e:
        st.error(f"An unexpected error occurred while running {script_name}: {e}")
        return False

def run_all_bots_sequentially():
    """
    Runs sel.py, then selass2.py, ensuring sequential execution.
    """
    if st.session_state.get('running_script', False):
        st.warning("A script sequence is already running. Please wait.")
        return

    st.session_state['running_script'] = True
    st.session_state['clear_console_on_next_sequence'] = True
    
    overall_status_placeholder = st.empty()
    script_output_placeholder = st.empty()

    with overall_status_placeholder.container():
        st.info("Starting sequential execution...")

    try:
        with overall_status_placeholder.container():
            st.info("Running `sel.py` (Spelling Bee Assignment)...")
        if run_script("sel.py", log_placeholder=script_output_placeholder):
            with overall_status_placeholder.container():
                st.info("`sel.py` completed. Running `selass2.py` (Full Assignment Creator)...")
            if run_script("selass2.py", log_placeholder=script_output_placeholder):
                with overall_status_placeholder.container():
                    st.success("✅ All automation scripts completed successfully!")
            else:
                with overall_status_placeholder.container():
                    st.error("❌ `selass2.py` failed. Sequential execution stopped.")
        else:
            with overall_status_placeholder.container():
                st.error("❌ `sel.py` failed. Sequential execution stopped.")
    except Exception as e:
        with overall_status_placeholder.container():
            st.error(f"An unexpected error occurred during sequential execution: {e}")
    finally:
        st.session_state['running_script'] = False
        read_and_display_logs() # Refresh logs after sequence

def read_and_display_logs():
    """Reads and displays log entries from the local JSONL file in a tabular format."""
    st.subheader("Automation Logs")
    
    if not os.path.exists(LOG_FILE_PATH):
        st.info(f"Log file not found at: `{LOG_FILE_PATH}`. Run the automation scripts first.")
        return

    log_entries_raw = []
    try:
        with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        log_entry = json.loads(line)
                        log_entries_raw.append(log_entry)
                    except json.JSONDecodeError:
                        st.warning(f"Skipping malformed log line: {line.strip()}")
                        continue
    except Exception as e:
        st.error(f"Error reading log file at `{LOG_FILE_PATH}`: {e}")
        return

    if not log_entries_raw:
        st.info("No log entries yet.")
        return

    # Sort logs by timestamp (newest first)
    log_entries_raw.sort(key=lambda x: x.get('asctime', x.get('timestamp', '')), reverse=True)

    # Prepare data for DataFrame
    log_data = []
    for entry in log_entries_raw:
        timestamp_str = entry.get('asctime', entry.get('timestamp', 'N/A'))
        # Format timestamp to show only time and maybe date if needed, otherwise just time
        if 'T' in timestamp_str and '.' in timestamp_str: # ISO format (e.g., from Streamlit logs)
            display_time = timestamp_str.split('T')[1].split('.')[0] # HH:MM:SS
            display_date = timestamp_str.split('T')[0]
        else: # Standard log format (e.g., from your file_logger)
            # Example: '2023-10-27 10:30:00,123' -> '10:30:00'
            parts = timestamp_str.split(' ')
            if len(parts) > 1 and ',' in parts[1]: # Check for comma in time part
                display_time = parts[1].split(',')[0]
                display_date = parts[0]
            else: # Fallback for unexpected formats
                display_time = timestamp_str
                display_date = "N/A"
        
        # Combine date and time if desired, or keep separate
        full_timestamp = f"{display_date} {display_time}" if display_date != "N/A" else display_time

        log_data.append({
            "Timestamp": full_timestamp,
            "Level": entry.get('levelname', 'N/A').upper(),
            "Script": entry.get('script_name', 'N/A'),
            "Message": entry.get('message', 'N/A'),
            "Run ID": entry.get('run_id', 'N/A'), # Include for detail if needed
            "Status": entry.get('status', 'N/A'), # Include for detail if needed
            "Screenshot": entry.get('screenshot', 'N/A'), # Path if exists
            "Traceback": entry.get('exc_info', 'N/A') # Traceback string
        })
    
    # Create DataFrame for tabular display
    df = pd.DataFrame(log_data)
    
    # Display the DataFrame
    st.dataframe(df[['Timestamp', 'Level', 'Script', 'Message']], use_container_width=True)

    # Optional: Display detailed logs in an expandable section below the table
    st.markdown("---")
    st.subheader("Detailed Log Entries")
    for entry_detail in log_entries_raw: # Iterate raw entries for full detail
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            timestamp_str = entry_detail.get('asctime', entry_detail.get('timestamp', 'N/A'))
            if 'T' in timestamp_str and '.' in timestamp_str:
                st.text(f"[{timestamp_str.split('T')[1].split('.')[0]}]")
            elif ' ' in timestamp_str and ',' in timestamp_str: # Handles your local logger format
                st.text(f"[{timestamp_str.split(' ')[1].split(',')[0]}]")
            else:
                st.text(f"[{timestamp_str}]")
        with col2:
            level = entry_detail.get('levelname', 'INFO').upper()
            level_color = "green"
            if level == "ERROR" or level == "CRITICAL":
                level_color = "red"
            elif level == "WARNING":
                level_color = "orange"
            st.markdown(f"<span style='color:{level_color};'>**{level}**</span>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"**{entry_detail.get('script_name', 'N/A')}**: {entry_detail.get('message', 'N/A')}")
        
        if 'run_id' in entry_detail:
            st.markdown(f"Run ID: `{entry_detail['run_id']}`")
        if 'status' in entry_detail:
            st.markdown(f"Status: **{entry_detail['status']}**")
        if 'screenshot' in entry_detail and entry_detail['screenshot'] != 'N/A': # Only show if a screenshot path exists
            st.info(f"Screenshot taken: `{entry_detail['screenshot']}`")
        if 'exc_info' in entry_detail and entry_detail['exc_info'] != 'N/A': # Only show if traceback exists
            with st.expander("Show Traceback"):
                st.code(entry_detail['exc_info'])
        st.markdown("---")


st.set_page_config(page_title="Selenium Automation Dashboard", layout="wide")
st.title("Selenium Automation Dashboard")

if 'stdout' not in st.session_state:
    st.session_state['stdout'] = []
if 'stderr' not in st.session_state:
    st.session_state['stderr'] = []
if 'running_script' not in st.session_state:
    st.session_state['running_script'] = False
if 'clear_console_on_next_sequence' not in st.session_state:
    st.session_state['clear_console_on_next_sequence'] = True

if st.button("Clear All Logs"):
    if os.path.exists(LOG_FILE_PATH):
        try:
            os.remove(LOG_FILE_PATH)
            st.success(f"Logs cleared successfully from `{LOG_FILE_PATH}`.")
            # This logic is now safer as LOG_DIR is well-defined
            if os.path.exists(LOG_DIR) and not os.listdir(LOG_DIR):
                os.rmdir(LOG_DIR)
        except Exception as e:
            st.error(f"Error clearing logs: {e}")
    else:
        st.info("No log file to clear.")
    # Use st.experimental_rerun() for a cleaner refresh
    st.experimental_rerun()

st.markdown("---")

st.write("### Run Selenium Bots Sequentially")
st.caption("This will run 'Spelling Bee Assignment' first, then 'Full Assignment Creator'.")

if st.button("Run All Bots Sequentially", use_container_width=True, disabled=st.session_state['running_script']):
    run_all_bots_sequentially()

if st.session_state['running_script']:
    st.info("Script sequence is running... Please wait for completion.")

if st.session_state['stdout'] or st.session_state['stderr']:
    st.subheader("Console Output from Last Sequential Run")
    if st.session_state['stdout']:
        st.code("\n".join(st.session_state['stdout']))
    if st.session_state['stderr']:
        st.error("\n".join(st.session_state['stderr']))

st.markdown("---")

# Display logs from the local file in tabular format
read_and_display_logs()

if st.button("Refresh Logs"):
    # Use st.experimental_rerun() to refresh the whole app state and log display
    st.experimental_rerun()

import sqlite3
import random
from datetime import datetime, timedelta

# --- Configuration ---
SOURCE_DB_FILE = "hosts.db"
SOURCE_TABLE_NAME = "hosts"

TARGET_DB_FILE = "logserver.db"
TARGET_TABLE_NAME = "logserver_hosts"
NUM_LOGSERVER_RECORDS = 70

def get_all_hosts():
    """Retrieves all host records from the source database."""
    conn = None
    try:
        conn = sqlite3.connect(SOURCE_DB_FILE)
        cursor = conn.cursor()
        cursor.execute(f"SELECT ip_address, hostname FROM {SOURCE_TABLE_NAME}")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error reading from source database: {e}")
        return []
    finally:
        if conn:
            conn.close()

def create_logserver_database_and_table():
    """Creates the logserver database and table if they don't exist."""
    conn = None
    try:
        conn = sqlite3.connect(TARGET_DB_FILE)
        cursor = conn.cursor()
        cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {TARGET_TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT NOT NULL,
            hostname TEXT NOT NULL,
            last_log_received_datetime TEXT NOT NULL
        )
        ''')
        conn.commit()
        print(f"Database '{TARGET_DB_FILE}' and table '{TARGET_TABLE_NAME}' are ready.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

def generate_random_datetime():
    """Generates a random datetime within a range (e.g., last 3 months to 1 year ago)."""
    end_date = datetime.now()
    # Simulate some hosts not sending logs for a long time (up to 1 year ago)
    # Or some recently (last 3 months)
    start_date_range_min = end_date - timedelta(days=365) # 1 year ago
    start_date_range_max = end_date - timedelta(days=90)  # 3 months ago

    # Randomly pick a start date within this range
    random_start_date = start_date_range_min + timedelta(days=random.randint(0, (start_date_range_max - start_date_range_min).days))

    time_diff = end_date - random_start_date
    random_seconds = random.uniform(0, time_diff.total_seconds())
    return (random_start_date + timedelta(seconds=random_seconds)).strftime("%Y-%m-%d %H:%M:%S")

def insert_logserver_data(selected_hosts):
    """Inserts the selected host data with random log reception times into the logserver database."""
    conn = None
    try:
        conn = sqlite3.connect(TARGET_DB_FILE)
        cursor = conn.cursor()

        records_to_insert = []
        for ip, hostname in selected_hosts:
            last_log_received = generate_random_datetime()
            records_to_insert.append((ip, hostname, last_log_received))

        cursor.executemany(f'''
        INSERT INTO {TARGET_TABLE_NAME} (ip_address, hostname, last_log_received_datetime)
        VALUES (?, ?, ?)
        ''', records_to_insert)

        conn.commit()
        print(f"Successfully inserted {len(selected_hosts)} records into '{TARGET_TABLE_NAME}'.")

    except sqlite3.Error as e:
        print(f"Database error during insertion: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Ensure hosts.db exists and has data first
    # You should run generate_data.py before running this script
    
    all_hosts = get_all_hosts()
    if not all_hosts:
        print("No hosts found in hosts.db. Please run generate_data.py first.")
    elif len(all_hosts) < NUM_LOGSERVER_RECORDS:
        print(f"Warning: Only {len(all_hosts)} hosts found, but {NUM_LOGSERVER_RECORDS} requested. Inserting all available hosts.")
        selected_hosts = all_hosts
    else:
        selected_hosts = random.sample(all_hosts, NUM_LOGSERVER_RECORDS)

    if selected_hosts:
        create_logserver_database_and_table()
        insert_logserver_data(selected_hosts)
        print("LogServer data generation process complete.")


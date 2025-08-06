
import sqlite3
import random
from datetime import datetime, timedelta

# --- Configuration ---
SOURCE_DB_FILE = "hosts.db"
SOURCE_TABLE_NAME = "hosts"

TARGET_DB_FILE = "antivirus.db"
TARGET_TABLE_NAME = "antivirus_hosts"
NUM_ANTIVIRUS_RECORDS = 80

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

def create_antivirus_database_and_table():
    """Creates the antivirus database and table if they don't exist."""
    conn = None
    try:
        conn = sqlite3.connect(TARGET_DB_FILE)
        cursor = conn.cursor()
        cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {TARGET_TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT NOT NULL,
            hostname TEXT NOT NULL,
            last_updated_datetime TEXT NOT NULL
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
    """Generates a random datetime within a range (e.g., last 2 years)."""
    end_date = datetime.now()
    # Simulate some hosts not updated for a long time (up to 2 years ago)
    start_date = end_date - timedelta(days=random.randint(0, 730)) # 730 days = 2 years
    
    time_diff = end_date - start_date
    random_seconds = random.uniform(0, time_diff.total_seconds())
    return (start_date + timedelta(seconds=random_seconds)).strftime("%Y-%m-%d %H:%M:%S")

def insert_antivirus_data(selected_hosts):
    """Inserts the selected host data with random update times into the antivirus database."""
    conn = None
    try:
        conn = sqlite3.connect(TARGET_DB_FILE)
        cursor = conn.cursor()

        records_to_insert = []
        for ip, hostname in selected_hosts:
            last_updated = generate_random_datetime()
            records_to_insert.append((ip, hostname, last_updated))

        cursor.executemany(f'''
        INSERT INTO {TARGET_TABLE_NAME} (ip_address, hostname, last_updated_datetime)
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
    elif len(all_hosts) < NUM_ANTIVIRUS_RECORDS:
        print(f"Warning: Only {len(all_hosts)} hosts found, but {NUM_ANTIVIRUS_RECORDS} requested. Inserting all available hosts.")
        selected_hosts = all_hosts
    else:
        selected_hosts = random.sample(all_hosts, NUM_ANTIVIRUS_RECORDS)

    if selected_hosts:
        create_antivirus_database_and_table()
        insert_antivirus_data(selected_hosts)
        print("Antivirus data generation process complete.")


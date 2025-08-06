
import sqlite3

# --- Configuration ---
HOSTS_DB = "hosts.db"
ANTIVIRUS_DB = "antivirus.db"
LOGSERVER_DB = "logserver.db"

DASHBOARD_DB = "dashboard.db"
DASHBOARD_TABLE = "dashboard_hosts"

def create_dashboard_table():
    """Creates the dashboard table in dashboard.db if it doesn't exist."""
    conn = None
    try:
        conn = sqlite3.connect(DASHBOARD_DB)
        cursor = conn.cursor()
        cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {DASHBOARD_TABLE} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT NOT NULL UNIQUE,
            hostname TEXT NOT NULL,
            purpose TEXT,
            classification TEXT,
            antivirus_last_updated TEXT, -- Can be NULL if no AV data
            logserver_last_received TEXT -- Can be NULL if no Log data
        )
        ''')
        conn.commit()
        print(f"Dashboard database '{DASHBOARD_DB}' and table '{DASHBOARD_TABLE}' are ready.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

def get_all_hosts_data():
    """Retrieves all host data from the hosts.db."""
    conn = None
    try:
        conn = sqlite3.connect(HOSTS_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT ip_address, hostname, purpose, classification FROM hosts")
        return {row[0]: {'hostname': row[1], 'purpose': row[2], 'classification': row[3]} for row in cursor.fetchall()}
    except sqlite3.Error as e:
        print(f"Error reading from hosts.db: {e}")
        return {}
    finally:
        if conn:
            conn.close()

def get_antivirus_data():
    """Retrieves antivirus data from antivirus.db."""
    conn = None
    try:
        conn = sqlite3.connect(ANTIVIRUS_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT ip_address, last_updated_datetime FROM antivirus_hosts")
        return {row[0]: row[1] for row in cursor.fetchall()}
    except sqlite3.Error as e:
        print(f"Error reading from antivirus.db: {e}")
        return {}
    finally:
        if conn:
            conn.close()

def get_logserver_data():
    """Retrieves logserver data from logserver.db."""
    conn = None
    try:
        conn = sqlite3.connect(LOGSERVER_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT ip_address, last_log_received_datetime FROM logserver_hosts")
        return {row[0]: row[1] for row in cursor.fetchall()}
    except sqlite3.Error as e:
        print(f"Error reading from logserver.db: {e}")
        return {}
    finally:
        if conn:
            conn.close()

def populate_dashboard_db():
    """Populates the dashboard database with consolidated data."""
    conn = None
    try:
        conn = sqlite3.connect(DASHBOARD_DB)
        cursor = conn.cursor()

        # Clear existing data for a fresh update
        cursor.execute(f"DELETE FROM {DASHBOARD_TABLE}")
        conn.commit()
        print(f"Cleared existing data in {DASHBOARD_TABLE}.")

        hosts_data = get_all_hosts_data()
        antivirus_data = get_antivirus_data()
        logserver_data = get_logserver_data()

        records_to_insert = []
        for ip, host_info in hosts_data.items():
            hostname = host_info['hostname']
            purpose = host_info['purpose']
            classification = host_info['classification']
            antivirus_last_updated = antivirus_data.get(ip) # None if not found
            logserver_last_received = logserver_data.get(ip) # None if not found

            records_to_insert.append((
                ip, hostname, purpose, classification,
                antivirus_last_updated, logserver_last_received
            ))
        
        if records_to_insert:
            cursor.executemany(f'''
            INSERT INTO {DASHBOARD_TABLE} (
                ip_address, hostname, purpose, classification,
                antivirus_last_updated, logserver_last_received
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ''', records_to_insert)
            conn.commit()
            print(f"Successfully inserted {len(records_to_insert)} records into '{DASHBOARD_TABLE}'.")
        else:
            print("No records to insert into dashboard database.")

    except sqlite3.Error as e:
        print(f"Database error during dashboard population: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_dashboard_table()
    populate_dashboard_db()
    print("Dashboard database update process complete.")

import sqlite3

DB_FILE = "hosts.db"
TABLE_NAME = "hosts"

def query_all():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {TABLE_NAME}")
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    conn.close()

if __name__ == "__main__":
    query_all()
